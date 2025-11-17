from sqlmodel import SQLModel
from typing import Optional

from app.modules.users.schemas import AuthorRead

class FriendRequestRead(SQLModel):
    """
    Schema para mostrar las "Solicitudes Recibidas".
    """
    id: int
    requester: AuthorRead

class FriendRequestCreate(SQLModel):
    """
    Schema de entrada para 'POST /friends/requests'.
    Define a quién se le envía la solicitud.
    """
    target_user_id: int