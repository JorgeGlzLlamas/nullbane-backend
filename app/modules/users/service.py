from fastapi import Depends, HTTPException, status
from sqlmodel import Session
from app.db.session import get_db
from app.modules.users import repository as user_repository
from app.modules.users.schemas import UserCreate
from app.modules.users.model import User
from app import auth_security

class UserService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def register_user(self, user_in: UserCreate) -> User:
        """
        Lógica de negocio para registrar un usuario.
        """

        # Verificar si el email ya existe
        user_by_email = user_repository.get_user_by_email(self.db, email=user_in.email)
        if user_by_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado.",
            )

        # Verificar si el username ya existe
        user_by_username = user_repository.get_user_by_username(self.db, username=user_in.username)
        if user_by_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya existe.",
            )

        # 1. Hashear la contraseña
        hashed_password = auth_security.get_password_hash(user_in.password)

        # 2. Llamar al repositorio para guardar
        return user_repository.create_user(self.db, user_in, hashed_password)