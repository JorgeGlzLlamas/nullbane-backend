from fastapi import APIRouter, Depends, status
from typing import List
from app.auth_security import get_current_user
from app.modules.users.model import User
# Usamos el nuevo schema
from .schemas import AchievementWithStatus, AchievementCreate, AchievementRead
from .service import AchievementService

router = APIRouter()

@router.get(
    "/",
    response_model=List[AchievementWithStatus],
    summary="Ver catálogo de logros (con mi estado)"
)
def get_achievements_catalog(
    current_user: User = Depends(get_current_user),
    service: AchievementService = Depends()
):
    """
    Devuelve TODOS los logros.
    Cada logro incluye un campo 'is_unlocked' (true/false)
    dependiendo de si el usuario actual lo tiene.
    """
    return service.get_catalog_with_status(current_user)

@router.post(
    "/",
    response_model=AchievementRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo logro (Solo Admin)"
)
def create_achievement(
    achievement_in: AchievementCreate,
    current_user: User = Depends(get_current_user),
    service: AchievementService = Depends()
):
    """
    Crea un nuevo logro en el sistema.
    Requiere ser Superusuario.
    """
    return service.create_new_achievement(current_user, achievement_in)

@router.post(
    "/{achievement_id}/unlock",
    status_code=status.HTTP_201_CREATED,
    summary="[DEV] Desbloquear un logro con el botón"
)
def unlock_achievement_dev(
    achievement_id: int,
    current_user: User = Depends(get_current_user),
    service: AchievementService = Depends()
):
    service.unlock_achievement(current_user.id, achievement_id)
    return {"message": "Logro desbloqueado"}
