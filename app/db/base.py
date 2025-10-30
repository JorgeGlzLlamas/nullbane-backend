from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """
    Clase Base para todos los modelos de SQLAlchemy.
    Todos los modelos (User, Post, etc.) heredarán de aquí.
    """
    pass

# NOTA: Más adelante, cuando crees tus modelos (ej. user_model.py),
# importaremos esta clase 'Base' allí.
# Y en *este* archivo, importaremos los modelos para que Alembic (migraciones)
# pueda verlos. Pero por ahora, esto es todo lo que necesita.