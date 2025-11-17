from sqlmodel import Field, Relationship, SQLModel
from app.db.base import BaseModel
from typing import Optional, TYPE_CHECKING

# Para evitar importación circular
if TYPE_CHECKING:
    from app.modules.users.model import User
    from app.modules.friendships.model import Friendship

class Message(BaseModel, table=True):
    __tablename__ = "message"

    content: str = Field(nullable=False)
    
    # A qué chat (amistad) pertenece
    friendship_id: int = Field(foreign_key="friendship.id", nullable=False)
    friendship: "Friendship" = Relationship(back_populates="messages")
    
    # Quién envió el mensaje
    sender_id: int = Field(foreign_key="user.id", nullable=False)
    sender: "User" = Relationship(back_populates="sent_messages")
