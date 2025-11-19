from sqlmodel import SQLModel
from datetime import datetime
from typing import Optional


class AchievementRead(SQLModel):
    id: int
    name: str
    description: str


class AchievementCreate(SQLModel):
    name: str
    description: str


class AchievementWithStatus(AchievementRead):
    """
    Hereda nombre y descripción, pero agrega el estado
    específico para el usuario que consulta.
    """
    is_unlocked: bool
    earned_at: datetime | None = None


class UserAchievementRead(SQLModel):
    """
    Muestra el logro anidado y cuándo se ganó.
    """
    achievement: AchievementRead 
    earned_at: datetime