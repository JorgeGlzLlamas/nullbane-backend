from fastapi import APIRouter, Depends, status
from app.modules.users.schemas import UserCreate, UserRead
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
    # Inyecta al "Guardia":
    # 1. Revisa el token (Bearer)
    # 2. Valida el token (firma, expiración)
    # 3. Busca al usuario en la BD
    # 4. Comprueba que 'is_active' sea True
    # 5. Si todo OK, devuelve el 'User' de la BD
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint protegido.
    Si llegas aquí, tu token es válido.
    Devuelve la información del usuario dueño del token.
    """
    return current_user