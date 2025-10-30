from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.settings import settings
from typing import Iterator

# Crear el engine
engine = create_engine(
    str(settings.DATABASE_URL),
    pool_pre_ping=True
)

# Fábrica de sesiones
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

# Dependencia de FastAPI
def get_db() -> Iterator[Session]:
    """
    Función 'dependencia' que inyecta una sesión de base de datos
    en los endpoints de la API.
    
    Asegura que la sesión se cierre siempre, incluso si hay un error.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()