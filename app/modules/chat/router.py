from fastapi import APIRouter, Depends, status, Query
from sqlmodel import Session
from typing import List, Optional

from app.db.session import get_db
from app.auth_security import get_current_user
from app.modules.users.model import User
from .schemas import ChatListRead, MessageRead, MessageCreate
from .service import ChatService

router = APIRouter()

@router.get(
    "/",
    response_model=List[ChatListRead],
    summary="Obtener lista de chats (Pantalla 1)"
)
def get_my_chat_list(
    search: Optional[str] = Query(None, description="Filtrar chats por nombre de amigo"),
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends()
):
    """
    Devuelve la lista de todos los chats 'aceptados' del usuario,
    ordenados por el mensaje más reciente.
    """
    return service.get_chat_list(current_user, search)

@router.get(
    "/{friendship_id}/messages",
    response_model=List[MessageRead],
    summary="Obtener mensajes de una conversación (Pantalla 2)"
)
def get_messages_for_chat(
    friendship_id: int,
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends()
):
    """
    Obtiene el historial de mensajes para un chat (amistad) específico.
    (Para Polling HTTP, el frontend debe llamar a esto periódicamente).
    """
    return service.get_messages(friendship_id, current_user)

@router.post(
    "/{friendship_id}/messages",
    response_model=MessageRead,
    status_code=status.HTTP_201_CREATED,
    summary="Enviar un mensaje (Pantalla 2)"
)
def send_message_to_chat(
    friendship_id: int,
    message_in: MessageCreate,
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends()
):
    """
    Envía un nuevo mensaje a un chat (amistad).
    Actualiza el 'last_message_at' del chat.
    """
    return service.send_message(friendship_id, message_in, current_user)
