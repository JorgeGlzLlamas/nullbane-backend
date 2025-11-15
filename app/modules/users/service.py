from fastapi import Depends, HTTPException, status, UploadFile
from sqlmodel import Session
from app.db.session import get_db
from app.modules.users import repository as user_repository
from app.modules.users.schemas import UserCreate, UserUpdate, UserChangePassword
from app.modules.users.model import User
from app import auth_security
import re
import shutil
import os
from uuid import uuid4


AVATAR_UPLOAD_DIR = "/data/avatars"
os.makedirs(AVATAR_UPLOAD_DIR, exist_ok=True)

# Límite de 2MB para el avatar
MAX_AVATAR_SIZE_MB = 2
MAX_AVATAR_SIZE_BYTES = MAX_AVATAR_SIZE_MB * 1024 * 1024
ALLOWED_AVATAR_MIMETYPE = "image/jpeg"

class UserService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def _generate_unique_username(self, first_name: str, last_name: str | None) -> str:
        """
        Genera un username único (ej: 'jorge.llamas', 'jorge.llamas1', ...)
        """
        # 1. Crea la base del username
        base_username = f"{first_name.lower()}"
        if last_name:
            cleaned_last = re.sub(r"[^a-z0-9]", "", last_name.lower())
            base_username = f"{first_name.lower()}.{cleaned_last}"
        
        base_username = re.sub(r"[^a-z0-9.]", "", base_username)[:30]

        username = base_username
        counter = 1
        while user_repository.get_user_by_username(self.db, username=username):
            username = f"{base_username}{counter}"
            counter += 1
            
        return username


    def register_user(self, user_in: UserCreate) -> User:
        """Lógica de negocio para registrar un usuario."""
        
        if user_repository.get_user_by_email(self.db, email=user_in.email):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "El email ya está registrado.")

        if user_in.password != user_in.confirm_password:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Las contraseñas no coinciden.")

        generated_username = self._generate_unique_username(
            first_name=user_in.first_name,
            last_name=user_in.last_name
        )
        
        hashed_password = auth_security.get_password_hash(user_in.password)
        
        return user_repository.create_user_with_settings(
            db=self.db,
            user_data=user_in,
            generated_username=generated_username,
            hashed_password=hashed_password
        )


    def change_password(
        self, 
        user: User, 
        password_data: UserChangePassword
    ) -> User:
        """
        Lógica de negocio para cambiar la contraseña de un usuario.
        """

        if not auth_security.verify_password(
            password_data.old_password, user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña antigua es incorrecta."
            )

        if password_data.new_password != password_data.confirm_new_password:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Las nuevas contraseñas no coinciden."
            )

        new_hashed_password = auth_security.get_password_hash(
            password_data.new_password
        )

        user.hashed_password = new_hashed_password
        return user_repository.update_user(self.db, user)


    def update_profile(self, user: User, update_data: UserUpdate) -> User:
        """Actualiza los campos de texto del perfil."""
        
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(user, key, value)
        return user_repository.update_user(self.db, user)


    def update_avatar(self, user: User, file: UploadFile) -> User:
        """Guarda un nuevo avatar y actualiza la URL en la BD."""

        if file.content_type != ALLOWED_AVATAR_MIMETYPE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Formato de imagen no válido. Solo se permite {ALLOWED_AVATAR_MIMETYPE} (JPG)."
            )

        file.file.seek(0, 2)
        file_size = file.file.tell()

        file.file.seek(0) 
        
        if file_size > MAX_AVATAR_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"El archivo es demasiado grande. Límite: {MAX_AVATAR_SIZE_MB}MB."
            )

        file_extension = ".jpg"
        file_name = f"avatar_user_{user.id}_{uuid4()}{file_extension}"
        file_path_on_disk = os.path.join(AVATAR_UPLOAD_DIR, file_name)
        file_url_path = f"/{AVATAR_UPLOAD_DIR}/{file_name}".replace("\\", "/")

        if user.avatar_url:
            old_path = user.avatar_url.lstrip("/")
            if os.path.exists(old_path):
                os.remove(old_path)

        try:
            with open(file_path_on_disk, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Error al guardar el archivo: {e}")

        user.avatar_url = file_url_path
        return user_repository.update_user(self.db, user)
