from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from .model import Achievement, UserAchievement
from .schemas import AchievementCreate

def get_all_achievements(db: Session) -> list[Achievement]:
    """Obtiene el catálogo completo de logros."""
    return db.exec(select(Achievement)).all()

def get_user_achievements(db: Session, user_id: int) -> list[UserAchievement]:
    """
    Obtiene los logros ganados por un usuario.
    """
    statement = (
        select(UserAchievement)
        .where(UserAchievement.user_id == user_id)
    )
    return db.exec(statement).all()

def get_achievement_by_id(db: Session, achievement_id: int) -> Achievement | None:
    return db.get(Achievement, achievement_id)

def get_user_achievement_link(db: Session, user_id: int, achievement_id: int) -> UserAchievement | None:
    """Verifica si el usuario ya tiene este logro."""
    statement = select(UserAchievement).where(
        UserAchievement.user_id == user_id,
        UserAchievement.achievement_id == achievement_id
    )
    return db.exec(statement).first()

def add_achievement_to_user(db: Session, user_id: int, achievement_id: int) -> UserAchievement:
    """Crea el vínculo entre usuario y logro."""
    link = UserAchievement(user_id=user_id, achievement_id=achievement_id)
    db.add(link)
    db.commit()
    db.refresh(link)
    return link

def get_achievement_by_name(db: Session, name: str) -> Achievement | None:
    """Busca un logro por su nombre único."""
    statement = select(Achievement).where(Achievement.name == name)
    return db.exec(statement).first()

def create_achievement(db: Session, achievement_in: AchievementCreate) -> Achievement:
    """Crea un nuevo logro en el catálogo."""
    # Convertimos el schema (Create) al modelo de BD
    db_achievement = Achievement.model_validate(achievement_in)
    db.add(db_achievement)
    db.commit()
    db.refresh(db_achievement)
    return db_achievement