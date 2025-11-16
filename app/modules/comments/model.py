from sqlmodel import Field, Relationship, SQLModel
from app.db.base import BaseModel # Importamos el BaseModel
from typing import Optional, TYPE_CHECKING

# Para evitar importaciones circulares
if TYPE_CHECKING:
    from app.modules.users.model import User
    from app.modules.posts.model import Post

class Comment(BaseModel, table=True):
    __tablename__ = "comment"

    content: str = Field(nullable=False)
    
    # --- Relación 1:N con User (Autor) ---
    author_id: int = Field(foreign_key="user.id", nullable=False)
    author: "User" = Relationship(back_populates="comments")

    # --- Relación 1:N con Post ---
    post_id: int = Field(foreign_key="post.id", nullable=False)
    post: "Post" = Relationship(back_populates="comments")