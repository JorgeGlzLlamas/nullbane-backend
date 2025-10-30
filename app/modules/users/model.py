from sqlmodel import Field
from app.db.base import BaseModel


class User(BaseModel, table=True):
    """Modelo de usuario"""

    email: str = Field(unique=True, index=True, nullable=False)
    username: str = Field(unique=True, index=True, nullable=False)
    hashed_password: str = Field(nullable=False)
    
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)