from sqlmodel import SQLModel
from datetime import datetime
from typing import List, Optional

from app.modules.users.schemas import AuthorRead
from app.modules.comments.schemas import CommentRead 


class PostRead(SQLModel):
    """
    Schema para leer una publicación (sin comentarios, para listas/feeds).
    Utiliza el 'AuthorRead' actualizado.
    """
    id: int
    title: str
    description: str
    image_url: str | None
    created_at: datetime
    updated_at: datetime
    author: AuthorRead


class PostReadWithComments(PostRead):
    """
    Schema completo para leer una publicación
    Y TODOS sus comentarios anidados.
    """
    comments: List[CommentRead] = []