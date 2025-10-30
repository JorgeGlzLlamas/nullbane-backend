from sqlmodel import SQLModel, Field
from app.db.base import BaseModel


class UserCreate(SQLModel):
    """
    Schema para crear un nuevo usuario.
    Solo contiene los campos que el usuario debe proveer.
    """

    email: str
    username: str
    password: str


class UserRead(BaseModel):
    """
    Schema para leer datos de un usuario.
    Incluye todos los campos que se pueden devolver en respuestas.
    """

    id: int
    email: str
    username: str
    is_active: bool
    is_superuser: bool
    created_at: str
    updated_at: str


class UserUpdate(SQLModel):
    """Schema para actualizar datos de un usuario."""

    email: str | None = None
    username: str | None = None
    password: str | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None