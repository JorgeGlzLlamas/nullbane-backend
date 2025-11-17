from sqlmodel import SQLModel, Field
from datetime import datetime
from pydantic import field_validator, ValidationInfo, EmailStr, computed_field

class UserCreate(SQLModel):
    """
    Schema para el formulario de registro.
    Valida que las contraseñas coincidan.
    """
    email: EmailStr
    first_name: str = Field(..., min_length=1)
    last_name: str | None = None
    password: str
    confirm_password: str

    @field_validator('confirm_password')
    def passwords_match(cls, v: str, info: ValidationInfo) -> str:
        """Valida que 'confirm_password' coincida con 'password'."""
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('Las contraseñas no coinciden')
        return v
    
    @field_validator('last_name')
    def empty_str_to_none(cls, v: str | None) -> str | None:
        """Convierte un string vacío "" en None."""
        if v == "":
            return None
        return v

class UserRead(SQLModel):
    """
    Schema para devolver los datos del usuario (perfil público/privado).
    No incluye la contraseña.
    """
    id: int
    email: EmailStr
    username: str
    first_name: str
    last_name: str | None
    phone_number: str | None
    avatar_url: str | None
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

class UserUpdate(SQLModel):
    """
    Schema para el formulario "Editar Perfil".
    Todos los campos son opcionales.
    Avatar se sube por un endpoint separado.
    """
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = None

class UserChangePassword(SQLModel):
    """
    Schema para el formulario de cambio de contraseña.
    Requiere la contraseña antigua y la nueva (con confirmación).
    """
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=72)
    confirm_new_password: str

    @field_validator('confirm_new_password')
    def passwords_match(cls, v: str, info: ValidationInfo) -> str:
        """Valida que 'confirm_new_password' coincida con 'new_password'."""
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('Las nuevas contraseñas no coinciden')
        return v

class AuthorRead(SQLModel):
    """
    Schema simplificado para mostrar el autor (usado en Post/Comment).
    Incluye el full_name concatenado.
    """
    id: int
    avatar_url: str | None
    first_name: str
    last_name: str | None

    @computed_field
    @property
    def full_name(self) -> str:
        """Concatena el nombre y el apellido."""
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name

class UserSearchRead(SQLModel):
    """
    Schema para los resultados de búsqueda en 'Agregar Amigos'.
    El backend ya ha filtrado a los amigos y pendientes.
    """
    id: int
    username: str
    avatar_url: str | None
    first_name: str
    last_name: str | None

    @computed_field
    @property
    def full_name(self) -> str:
        """Concatena el nombre y el apellido."""
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name
