from sqlmodel import Session, select
from app.modules.users.model import User
from app.modules.users.schemas import UserCreate


def get_user_by_email(db: Session, email: str) -> User | None:
    """Busca un usuario por su email."""
    statement = select(User).where(User.email == email)
    return db.exec(statement).first()


def get_user_by_username(db: Session, username: str) -> User | None:
    """Busca un usuario por su username."""
    statement = select(User).where(User.username == username)
    return db.exec(statement).first()


def create_user(db: Session, user_in: UserCreate, hashed_password: str) -> User:
    """
    Crea un nuevo usuario en la BD.
    Usa los valores por defecto del modelo para 'is_active' y 'is_superuser'.
    """

    db_user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=hashed_password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user