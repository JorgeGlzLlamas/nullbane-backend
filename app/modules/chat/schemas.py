from sqlmodel import SQLModel
from datetime import datetime
from typing import List, Optional

from app.modules.users.schemas import AuthorRead


class ChatListRead(SQLModel):
    """
    Representa un chat en la lista principal (estilo WhatsApp).
    """
    friendship_id: int # El ID para abrir el chat
    other_user: AuthorRead # La persona con la que estás chateando
    last_message_content: str | None # El último mensaje (para vista previa)
    last_message_at: datetime | None # Para ordenar la lista


class MessageRead(SQLModel):
    """
    Representa un solo mensaje dentro de una conversación.
    """
    id: int
    content: str
    sender_id: int
    created_at: datetime


class MessageCreate(SQLModel):
    """
    Schema de entrada para enviar un mensaje nuevo.
    """
    content: str