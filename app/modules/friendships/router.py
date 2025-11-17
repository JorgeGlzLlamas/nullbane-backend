from fastapi import APIRouter, Depends, status, Response, Query
from sqlmodel import Session, SQLModel
from typing import List

from app.db.session import get_db
from app.auth_security import get_current_user
from app.modules.users.model import User
from app.modules.users.schemas import UserSearchRead
from .schemas import FriendRequestRead, FriendRequestCreate
from .service import FriendshipService

router = APIRouter()


class FriendRequestCreate(SQLModel):
    target_user_id: int

@router.get(
    "/search",
    response_model=List[UserSearchRead],
    summary="Buscar usuarios para agregar (Pantalla 3)"
)
def search_users_to_add(
    name: str = Query(..., min_length=1, description="Nombre a buscar (ej. 'jorge' o 'jorge ll')"),
    current_user: User = Depends(get_current_user),
    service: FriendshipService = Depends()
):
    """
    Busca usuarios por nombre/apellido (istartswith, case-insensitive).
    Filtra automáticamente:
    - Al usuario actual
    - Usuarios que ya son amigos
    - Usuarios con solicitudes pendientes (enviadas o recibidas)
    """
    return service.search_potential_friends(current_user, name)

@router.get(
    "/requests/received",
    response_model=List[FriendRequestRead],
    summary="Obtener solicitudes de amistad recibidas (Pantalla 3)"
)
def get_received_friend_requests(
    current_user: User = Depends(get_current_user),
    service: FriendshipService = Depends()
):
    """Devuelve la lista de solicitudes pendientes que el usuario actual puede aceptar."""
    return service.get_received_requests(current_user)

@router.post(
    "/requests",
    status_code=status.HTTP_201_CREATED,
    summary="Enviar una solicitud de amistad (Pantalla 3)"
)
def send_friend_request(
    request_data: FriendRequestCreate,
    current_user: User = Depends(get_current_user),
    service: FriendshipService = Depends()
):
    """Envía una solicitud de amistad a otro usuario."""
    service.send_friend_request(current_user, request_data.target_user_id)
    return {"message": "Solicitud enviada."}

@router.post(
    "/requests/{friendship_id}/accept",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Aceptar una solicitud de amistad (Pantalla 3)"
)
def accept_friend_request(
    friendship_id: int,
    current_user: User = Depends(get_current_user),
    service: FriendshipService = Depends()
):
    """Acepta una solicitud de amistad. Habilita el chat."""
    service.accept_friend_request(friendship_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.delete(
    "/requests/{friendship_id}/reject",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Rechazar una solicitud de amistad (Pantalla 3)"
)
def reject_friend_request(
    friendship_id: int,
    current_user: User = Depends(get_current_user),
    service: FriendshipService = Depends()
):
    """Rechaza (elimina) una solicitud de amistad."""
    service.reject_friend_request(friendship_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
