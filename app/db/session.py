from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.core.settings import settings

# Crear el engine
engine = create_engine(
    str(settings.DATABASE_URL),
    pool_pre_ping=True
)


# Dependencia de FastAPI
def get_db():
    """
    Función 'dependencia' que inyecta una sesión de base de datos
    en los endpoints de la API.
    
    Asegura que la sesión se cierre siempre, incluso si hay un error.
    """
    with Session(engine) as session:
        yield session
