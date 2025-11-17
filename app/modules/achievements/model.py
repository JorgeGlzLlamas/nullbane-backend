from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint
from app.db.base import BaseModel
from typing import Optional, List, TYPE_CHECKING

# Para evitar importaciones circulares
if TYPE_CHECKING:
    from app.modules.users.model import User

# --- TABLA PIVOTE (El Vínculo) ---
class UserAchievement(BaseModel, table=True):
    """
    Tabla intermedia que registra qué usuarios tienen qué logros.
    Hereda de BaseModel, así que 'created_at' nos dice CUÁNDO lo ganó.
    """
    __tablename__ = "user_achievement"
    
    __table_args__ = (
        UniqueConstraint("user_id", "achievement_id", name="uq_user_achievement"),
    )

    user_id: int = Field(foreign_key="user.id", nullable=False)
    achievement_id: int = Field(foreign_key="achievement.id", nullable=False)

    # Relaciones para navegar desde el pivote
    user: "User" = Relationship(back_populates="achievements_link")
    achievement: "Achievement" = Relationship(back_populates="users_link")


# --- TABLA CATÁLOGO  ---
class Achievement(BaseModel, table=True):
    """Catálogo de logros disponibles en el sistema."""
    __tablename__ = "achievement"

    name: str = Field(unique=True, index=True, nullable=False)
    description: str = Field(nullable=False)

    # Relación N:N con User a través de UserAchievement
    users_link: List["UserAchievement"] = Relationship(back_populates="achievement")
