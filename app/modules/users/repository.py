from sqlmodel import Session, select
from app.modules.users.model import User
from app.modules.users.schemas import UserCreate
from app.modules.settings.model import Settings


def get_user_by_email(db: Session, email: str) -> User | None:
    """Busca un usuario por su email."""
    statement = select(User).where(User.email == email)
    return db.exec(statement).first()


def get_user_by_username(db: Session, username: str) -> User | None:
    """Busca un usuario por su username (para el generador)."""
    statement = select(User).where(User.username == username)
    return db.exec(statement).first()


def create_user_with_settings(
    db: Session, 
    user_data: UserCreate,
    generated_username: str,
    hashed_password: str
) -> User:
    """
    Crea el Usuario y sus Settings por defecto en una sola transacción.
    """
    
    db_user = User(
        email=user_data.email,
        username=generated_username,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        is_active=True,
        is_superuser=False
    )
    
    db_settings = Settings(
        user=db_user
    )

    db.add(db_user)
    db.add(db_settings)
    

    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_to_update: User) -> User:
    """
    Guarda un objeto de usuario que ya fue modificado en el servicio.
    """
    db.add(user_to_update)
    db.commit()
    db.refresh(user_to_update)
    return user_to_update