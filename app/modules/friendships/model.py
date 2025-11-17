import datetime
from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint
from app.db.base import BaseModel
from typing import Optional, TYPE_CHECKING, List
from sqlalchemy import Column, DateTime, func

if TYPE_CHECKING:
    from app.modules.users.model import User
    from app.modules.chat.model import Message

class Friendship(BaseModel, table=True):
    """
    Modelo que representa tanto una solicitud de amistad como
    un chat activo (amistad aceptada).
    """
    __tablename__ = "friendship"

    __table_args__ = (
        UniqueConstraint("user_1_id", "user_2_id", name="uq_friendship_users"),
    )

    user_1_id: int = Field(foreign_key="user.id", nullable=False)
    user_2_id: int = Field(foreign_key="user.id", nullable=False)
    
    # Estado de la amistad
    status: str = Field(default="pendiente", nullable=False)

    action_user_id: int = Field(foreign_key="user.id", nullable=False)
    
    last_message_at: datetime.datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True))
    )

    user1: "User" = Relationship(
        back_populates="friendships_as_user1",
        sa_relationship_kwargs={"foreign_keys": "[Friendship.user_1_id]"}
    )
    user2: "User" = Relationship(
        back_populates="friendships_as_user2",
        sa_relationship_kwargs={"foreign_keys": "[Friendship.user_2_id]"}
    )
    
    messages: List["Message"] = Relationship(back_populates="friendship")