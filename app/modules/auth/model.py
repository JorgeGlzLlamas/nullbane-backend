from sqlmodel import SQLModel, Field
from app.db.base import BaseModel
from datetime import datetime
from sqlalchemy import Column, DateTime

class PasswordReset(BaseModel, table=True):
    """
    Tabla temporal para guardar códigos de recuperación.
    """
    __tablename__ = "password_reset"

    email: str = Field(index=True, nullable=False)
    code: str = Field(nullable=False)
    expires_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
