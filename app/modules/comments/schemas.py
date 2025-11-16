from sqlmodel import SQLModel
from datetime import datetime
from app.modules.users.schemas import AuthorRead 


class CommentCreate(SQLModel):
    """
    Schema para crear un nuevo comentario.
    El frontend solo necesita enviar el contenido.
    """
    content: str


class CommentRead(SQLModel):
    """
    Schema para leer un comentario, incluyendo su autor.
    """
    id: int
    content: str
    created_at: datetime
    updated_at: datetime
    post_id: int
    author: AuthorRead