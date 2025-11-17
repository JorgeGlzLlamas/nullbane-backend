from sqlmodel import Field, Relationship, SQLModel
from app.db.base import BaseModel
from typing import Optional, TYPE_CHECKING, List
from datetime import datetime
from sqlalchemy import Column, DateTime, func

# Para evitar importación circular
if TYPE_CHECKING:
    from app.modules.settings.model import Settings
    from app.modules.posts.model import Post
    from app.modules.comments.model import Comment
    from app.modules.friendships.model import Friendship
    from app.modules.chat.model import Message

class User(BaseModel, table=True):
    __tablename__ = "user"

    email: str = Field(unique=True, index=True, nullable=False)
    username: str = Field(unique=True, index=True, nullable=False)
    hashed_password: str = Field(nullable=False)
    first_name: str = Field(nullable=False)
    last_name: str | None = Field(default=None)
    phone_number: str | None = Field(default=None, unique=True, index=True)
    avatar_url: str | None = Field(default=None) 
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    
    settings: Optional["Settings"] = Relationship(
        back_populates="user", 
        sa_relationship_kwargs={"uselist": False}
    )
    posts: List["Post"] = Relationship(back_populates="author")
    comments: List["Comment"] = Relationship(back_populates="author")

    # Amistades donde el usuario es 'user_1' (el ID más bajo)
    friendships_as_user1: List["Friendship"] = Relationship(
        back_populates="user1",
        sa_relationship_kwargs={"foreign_keys": "Friendship.user_1_id"}
    )
    # Amistades donde el usuario es 'user_2' (el ID más alto)
    friendships_as_user2: List["Friendship"] = Relationship(
        back_populates="user2",
        sa_relationship_kwargs={"foreign_keys": "Friendship.user_2_id"}
    )

    sent_messages: List["Message"] = Relationship(back_populates="sender")