from sqlmodel import SQLModel
from typing import Literal

ThemeOptions = Literal["light", "dark"]
LanguageOptions = Literal["es", "en"]

class SettingsRead(SQLModel):
    """Schema para leer las configuraciones del usuario."""
    theme: ThemeOptions
    language: LanguageOptions
    user_id: int


class SettingsUpdate(SQLModel):
    """Schema para actualizar las configuraciones (todos opcionales)."""
    theme: ThemeOptions | None = None
    language: LanguageOptions | None = None