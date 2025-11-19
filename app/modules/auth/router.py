from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from datetime import datetime, timedelta, timezone
from app.db.session import get_db
from app import auth_security
from app.core.settings import settings
from app.modules.users.model import User
from app.modules.users.schemas import UserRead
from app.modules.users import repository as user_repository
from app.modules.auth.model import PasswordReset
from app.services import email_service
from app.modules.auth.schema import Token, AccessTokenOnly, RefreshRequest, PromoteRequest, ForgotPasswordRequest, ResetPasswordWithCodeRequest, VerifyCodeRequest


router = APIRouter()

@router.post(
    "/login/token", 
    response_model=Token,
    summary="Inicio de sesión para obtener token JWT"
)
def login_for_access_token(
    db: Session = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Inicia sesión con 'email' y 'password'.
    NOTA: El email debe enviarse en el campo 'username' del formulario.
    """

    user = user_repository.get_user_by_email(db, email=form_data.username)

    if not user or not auth_security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            # Mensaje de error actualizado
            detail="Email o contraseña incorrectos", 
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Usuario inactivo"
        )

    access_token = auth_security.create_access_token(
        data={"sub": user.email} 
    )
    refresh_token = auth_security.create_refresh_token(
        data={"sub": user.email}
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post(
    "/refresh", 
    response_model=AccessTokenOnly,
    summary="Refresca el token de acceso"
)
def refresh_access_token(
    request_data: RefreshRequest,
    db: Session = Depends(get_db)
):
    """
    Obtiene un nuevo Access Token usando el Refresh Token.
    """
    # El 'guardia' valida el refresh token (que contiene el email)
    # y devuelve el objeto User
    user = auth_security.get_user_from_refresh_token_string(
        db, token_string=request_data.refresh_token
    )
    
    # --- ¡CAMBIO 3: Guardar Email en el nuevo Token! ---
    new_access_token = auth_security.create_access_token(
        data={"sub": user.email}
    )
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }

@router.post(
    "/promote-me",
    response_model=UserRead,
    summary="[DEV ONLY] Promover al usuario autenticado a Superusuario"
)
def promote_me_to_admin(
    promo_data: PromoteRequest, # El body que contiene el secreto
    current_user: User = Depends(auth_security.get_current_user), # El usuario a promover
    db: Session = Depends(get_db)
):
    """
    Endpoint de desarrollo para promover al usuario autenticado
    a superusuario. Requiere una clave secreta del servidor.
    """

    if promo_data.secret_key != settings.ADMIN_PROMOTION_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Clave secreta de promoción incorrecta."
        )
    current_user.is_superuser = True
    updated_user = user_repository.update_user(db, current_user)
    
    return updated_user

@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    request: ForgotPasswordRequest,
    background_tasks: BackgroundTasks, # Para enviar el email sin bloquear
    db: Session = Depends(get_db)
):
    # Validar que el usuario existe
    user = user_repository.get_user_by_email(db, email=request.email)
    if not user:
        # Respondemos OK por seguridad (User Enumeration Attack)
        return {"message": "Si el correo existe, se envió el código."}

    # Generar código
    otp_code = email_service.generate_otp_code()
    expires = datetime.now(timezone.utc) + timedelta(minutes=15)

    # Guardar o Actualizar en la tabla PasswordReset
    # Primero buscamos si ya tenía un código activo y lo borramos
    existing = db.exec(select(PasswordReset).where(PasswordReset.email == request.email)).first()
    if existing:
        db.delete(existing)
    
    # Creamos el nuevo registro
    reset_entry = PasswordReset(
        email=request.email,
        code=otp_code,
        expires_at=expires
    )
    db.add(reset_entry)
    db.commit()

    # Enviar Email (en segundo plano para que la respuesta sea rápida)
    background_tasks.add_task(
        email_service.send_password_reset_email, 
        request.email, 
        otp_code
    )

    return {"message": "Código enviado correctamente"}


@router.post("/verify-code", status_code=status.HTTP_200_OK)
def verify_reset_code(
    request: VerifyCodeRequest,
    db: Session = Depends(get_db)
):
    """
    Verifica si el código OTP es válido y no ha expirado.
    Se usa antes de permitir al usuario escribir su nueva contraseña.
    """
    reset_entry = db.exec(
        select(PasswordReset).where(
            PasswordReset.email == request.email,
            PasswordReset.code == request.code
        )
    ).first()

    if not reset_entry:

        raise HTTPException(status_code=400, detail="Código inválido")

    now_utc = datetime.now(timezone.utc)
    # Forzamos que la fecha de la BD sea interpretada como UTC si no tiene zona
    db_expire = reset_entry.expires_at
    if db_expire.tzinfo is None:
        db_expire = db_expire.replace(tzinfo=timezone.utc)

    if now_utc > db_expire:
        raise HTTPException(status_code=400, detail="El código ha expirado")

    return {"message": "Código válido"}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password_with_code(
    request: ResetPasswordWithCodeRequest,
    db: Session = Depends(get_db)
):
    # 1. Validar que las contraseñas coincidan
    if request.new_password != request.confirm_password:
        raise HTTPException(status_code=400, detail="Las contraseñas no coinciden")

    # 2. Buscar el código en la BD
    reset_entry = db.exec(
        select(PasswordReset).where(
            PasswordReset.email == request.email,
            PasswordReset.code == request.code
        )
    ).first()

    # --- VALIDACIONES CON LOGS DE DEPURACIÓN ---
    
    # A. Verificar existencia
    if not reset_entry:
        print("\n[DEBUG] Error: No se encontró entrada en PasswordReset para este email/código.")
        raise HTTPException(status_code=400, detail="Código inválido")

    # B. Verificar expiración con manejo de Timezones
    now_utc = datetime.now(timezone.utc)
    db_expire = reset_entry.expires_at
    
    # Si la BD devuelve la fecha sin zona horaria (naive), asumimos UTC
    if db_expire.tzinfo is None:
        db_expire = db_expire.replace(tzinfo=timezone.utc)

    if now_utc > db_expire:
        raise HTTPException(status_code=400, detail="El código ha expirado")

    # 3. Obtener usuario
    user = user_repository.get_user_by_email(db, email=request.email)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # 4. Actualizar contraseña
    user.hashed_password = auth_security.get_password_hash(request.new_password)
    user_repository.update_user(db, user)

    # 5. Borrar el código usado
    db.delete(reset_entry)
    db.commit()

    return {"message": "Contraseña restablecida con éxito"}
