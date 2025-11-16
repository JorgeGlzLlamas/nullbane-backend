from sqlmodel import Field, Relationship, SQLModel
from app.db.base import BaseModel # Importamos el BaseModel (id, created_at, updated_at)
from typing import Optional, List, TYPE_CHECKING

# Para evitar importaciones circulares
if TYPE_CHECKING:
    from app.modules.users.model import User
    from app.modules.comments.model import Comment

class Post(BaseModel, table=True):
    __tablename__ = "post"

    title: str = Field(nullable=False)
    description: str = Field(nullable=False)
    image_url: str | None = Field(default=None) 
    
    # --- Relación 1:N con User (Autor) ---
    author_id: int = Field(foreign_key="user.id", nullable=False)
    author: "User" = Relationship(back_populates="posts")
    
    # --- Relación 1:N con Comment ---
    comments: List["Comment"] = Relationship(back_populates="post")