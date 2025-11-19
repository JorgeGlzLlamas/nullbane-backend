from fastapi import Depends, HTTPException, status
from sqlmodel import Session
from app.db.session import get_db
from app.modules.users.model import User
from .model import Settings
from .schemas import SettingsUpdate
from . import repository as settings_repository


class SettingsService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def get_user_settings(self, user: User) -> Settings:
        """
        Obtiene las configuraciones del usuario.
        Gracias al 'selectinload' en el guardia,
        user.settings ya está cargado.
        """
        if not user.settings:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Configuraciones no encontradas")
        return user.settings


    def update_user_settings(self, user: User, update_data: SettingsUpdate) -> Settings:
        """
        Actualiza las configuraciones del usuario.
        Solo actualiza los campos que vienen en el JSON.
        """
        settings = user.settings

        update_dict = update_data.model_dump(exclude_unset=True)

        for key, value in update_dict.items():
            setattr(settings, key, value)
            
        # 3. Guarda en la BD
        return settings_repository.update_settings(self.db, settings)