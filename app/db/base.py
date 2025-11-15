# app/models/base.py
import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime
from sqlalchemy.orm import declarative_mixin, declared_attr

def get_utc_now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


@declarative_mixin
class TimestampMixin:
    """Mixin declarativo de SQLAlchemy que crea una Column por cada clase."""

    @declared_attr
    def created_at(cls):
        # Devuelve una NUEVA instancia Column para cada clase que herede.
        return Column(
            DateTime(timezone=True),
            nullable=False,
            default=get_utc_now,
        )

    @declared_attr
    def updated_at(cls):
        return Column(
            DateTime(timezone=True),
            nullable=False,
            default=get_utc_now,
            onupdate=get_utc_now,
        )


class BaseModel(TimestampMixin, SQLModel):
    """
    BaseModel que combina el mixin declarativo con SQLModel.
    NOTA: el orden de herencia es importante (mixin antes de SQLModel).
    """

    id: int | None = Field(default=None, primary_key=True, index=True)
