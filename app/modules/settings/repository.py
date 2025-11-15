from sqlmodel import Session
from app.modules.settings.model import Settings


def update_settings(db: Session, settings_obj: Settings) -> Settings:
    """Guarda los cambios del objeto Settings en la BD."""
    db.add(settings_obj)
    db.commit()
    db.refresh(settings_obj)
    return settings_obj