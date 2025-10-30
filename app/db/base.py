import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime


# Función helper para obtener la hora UTC
def get_utc_now() -> datetime.datetime:
    """Devuelve la fecha y hora actual en UTC con zona horaria."""
    return datetime.datetime.now(datetime.timezone.utc)


# Modelo base
class BaseModel(SQLModel):
    """
    Modelo base que incluye campos comunes para todas las tablas.
    No se convierte en tabla, sirve como "mixin" para otros modelos.
    """

    id: int | None = Field(default=None, primary_key=True, index=True)

    created_at: datetime.datetime = Field(
        default_factory=get_utc_now,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            default=get_utc_now,
        )
    )

    updated_at: datetime.datetime = Field(
        default_factory=get_utc_now,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            default=get_utc_now,
            onupdate=get_utc_now,
        )
    )