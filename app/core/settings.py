from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, model_validator
from typing import Optional

class Settings(BaseSettings):
    """
    Carga y valida las variables de entorno de la aplicación
    desde el archivo .env
    """

    # Configuración de Base de Datos
    DATABASE_URL: PostgresDsn | str | None = None

    DB_HOST: str | None = None
    DB_NAME: str | None = None
    DB_PORT: int | None = None
    DB_USER: str | None = None
    DB_PASSWORD: str | None = None


    @model_validator(mode='after')
    def get_database_url(self) -> 'Settings':
        """
        Validador que se ejecuta después de cargar las variables.
        Construye la DATABASE_URL si no se proveyó directamente.
        """

        if isinstance(self.DATABASE_URL, (str, PostgresDsn)):
            if isinstance(self.DATABASE_URL, str):
                if self.DATABASE_URL.startswith("postgresql://"):
                    self.DATABASE_URL = self.DATABASE_URL.replace(
                        "postgresql://", "postgresql+psycopg://", 1
                    )
            
            elif isinstance(self.DATABASE_URL, PostgresDsn):
                 if self.DATABASE_URL.scheme == "postgresql":
                    self.DATABASE_URL = PostgresDsn.build(
                        scheme="postgresql+psycopg",
                        username=self.DATABASE_URL.username,
                        password=self.DATABASE_URL.password,
                        host=self.DATABASE_URL.host,
                        port=self.DATABASE_URL.port,
                        path=self.DATABASE_URL.path,
                    )
                    
            return self

        
        if all([self.DB_HOST, self.DB_NAME, self.DB_PORT, self.DB_USER, self.DB_PASSWORD is not None]):
            self.DATABASE_URL = PostgresDsn.build(
                scheme="postgresql+psycopg",
                username=self.DB_USER,
                password=self.DB_PASSWORD,
                host=self.DB_HOST,
                port=self.DB_PORT,
                path=self.DB_NAME,
            )
            return self
        
        raise ValueError("Configuración de base de datos inválida. "
                         "Define DATABASE_URL (para Railway) o "
                         "DB_HOST, DB_NAME, DB_PORT, DB_USER, DB_PASSWORD (para local).")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Se crea una instancia única que se importará en otros archivos
settings = Settings()