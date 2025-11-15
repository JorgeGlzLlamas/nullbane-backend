from fastapi import APIRouter, Depends
from .schemas import SettingsRead, SettingsUpdate
from .service import SettingsService
from app.modules.users.model import User
from app.auth_security import get_current_user

router = APIRouter()

@router.get(
    "/me",
    response_model=SettingsRead,
    summary="Obtener configuraciones del usuario actual"
)
def get_my_settings(
    current_user: User = Depends(get_current_user),
    service: SettingsService = Depends()
):
    """
    Devuelve el tema ('light'/'dark') y el idioma ('es'/'en')
    del usuario autenticado.
    """
    return service.get_user_settings(user=current_user)

@router.put(
    "/me",
    response_model=SettingsRead,
    summary="Actualizar configuraciones del usuario actual"
)
def update_my_settings(
    update_data: SettingsUpdate,
    current_user: User = Depends(get_current_user),
    service: SettingsService = Depends()
):
    """
    Actualiza el tema o el idioma del usuario.
    Solo envía los campos que quieras cambiar.
    Ejemplo: {"theme": "dark"}
    """
    return service.update_user_settings(user=current_user, update_data=update_data)