from sqlmodel import Field, Relationship, SQLModel
from app.db.base import BaseModel
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.modules.users.model import User

class Settings(BaseModel, table=True):
    __tablename__ = "settings"

    user_id: int = Field(
        foreign_key="user.id",
        primary_key=True,
        nullable=False
    )
    user: "User" = Relationship(back_populates="settings")

    theme: str = Field(default="light", nullable=False)
    language: str = Field(default="es", nullable=False)

    # Sobrescribimos el 'id' de BaseModel para que no lo use
    id: Optional[int] = Field(default=None, primary_key=False)