from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from app.core.settings import settings
from app.db.session import get_db
from app import auth_security
from app.modules.users import repository as user_repository
from app.modules.users.model import User
from app.modules.auth.schema import Token, AccessTokenOnly, RefreshRequest

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
    Inicia sesión con 'username' y 'password' (en un form-data).
    Devuelve un token de acceso si las credenciales son válidas.
    """

    user = user_repository.get_user_by_username(db, username=form_data.username)

    if not user or not auth_security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre de usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Usuario inactivo"
        )

    access_token = auth_security.create_access_token(
        data={"sub": user.username}
    )
    refresh_token = auth_security.create_refresh_token(
        data={"sub": user.username}
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
    Obtiene un nuevo Access Token (de corta duración)
    usando el Refresh Token (de larga duración) enviado
    en una cookie HttpOnly.
    """
    user = auth_security.get_user_from_refresh_token_string(
        db, token_string=request_data.refresh_token
    )
    new_access_token = auth_security.create_access_token(data={"sub": user.username})
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }
