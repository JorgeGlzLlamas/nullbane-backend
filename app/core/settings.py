from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, computed_field
from typing import Optional

class Settings(BaseSettings):
    """
    Carga y valida las variables de entorno de la aplicación
    desde el archivo .env
    """
    
    # Carga el archivo .env en la raíz del proyecto
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Configuración de Base de Datos
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    @computed_field
    @property
    def DATABASE_URL(self) -> PostgresDsn:
        """
        Construye la URL de conexión de PostgreSQL a partir de las
        variables individuales.
        """
        return PostgresDsn.build(
            scheme="postgresql+psycopg",
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            path=self.DB_NAME,
        )

# Se crea una instancia única que se importará en otros archivos
settings = Settings()