from fastapi import APIRouter, Depends, status, UploadFile, File, Response
from app.modules.users.schemas import UserCreate, UserRead, UserUpdate, UserChangePassword
from app.modules.users.service import UserService
from app.modules.users.model import User
from app.auth_security import get_current_user

router = APIRouter()

@router.post(
    "/", 
    response_model=UserRead, 
    status_code=status.HTTP_201_CREATED,
    summary="Registro de un nuevo usuario"
)
def register_user(
    user_in: UserCreate, 
    service: UserService = Depends()
):
    """
    Endpoint para crear un nuevo usuario en el sistema.
    """
    return service.register_user(user_in)


@router.get(
    "/me", 
    response_model=UserRead,
    summary="Obtener datos del usuario autenticado"
)
def get_user_me(
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint protegido.
    Si llegas aquí, tu token es válido.
    Devuelve la información del usuario dueño del token.
    """
    return current_user


@router.put(
    "/me",
    response_model=UserRead,
    summary="Actualizar perfil del usuario (nombre, teléfono)"
)
def update_user_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends()
):
    """
    Actualiza el perfil del usuario (firstName, lastName, phoneNumber).
    Email y Avatar se actualizan en endpoints separados.
    """
    return service.update_profile(user=current_user, update_data=update_data)


@router.put(
    "/me/avatar",
    response_model=UserRead,
    summary="Actualizar el avatar del usuario"
)
def upload_avatar(
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(),
    file: UploadFile = File(..., description="Archivo de imagen (JPG o PNG)")
):
    """
    Sube un nuevo avatar para el usuario.
    Reemplaza el avatar anterior si existe.
    """
    return service.update_avatar(user=current_user, file=file)


@router.post(
    "/me/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cambiar la contraseña del usuario"
)
def update_user_password(
    password_data: UserChangePassword,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends()
):
    """
    Cambia la contraseña del usuario autenticado.
    Requiere la contraseña antigua y la nueva (con confirmación).
    """
    service.change_password(user=current_user, password_data=password_data)
    # No devolvemos nada en el body, solo un 204
    return Response(status_code=status.HTTP_204_NO_CONTENT)