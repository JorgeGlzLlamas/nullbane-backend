from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from sqlalchemy import or_, and_
from typing import Dict, Any

from .model import Friendship
from app.modules.users.model import User

def get_friendship_by_users(db: Session, user_id_1: int, user_id_2: int) -> Friendship | None:
    """Busca una amistad existente entre dos usuarios."""
    # Asegura el orden (bajo primero, alto después)
    low_id = min(user_id_1, user_id_2)
    high_id = max(user_id_1, user_id_2)
    
    statement = select(Friendship).where(
        Friendship.user_1_id == low_id,
        Friendship.user_2_id == high_id
    )
    return db.exec(statement).first()

def create_friend_request(
    db: Session, 
    user_1_id: int, 
    user_2_id: int, 
    action_user_id: int
) -> Friendship:
    """Crea un nuevo registro de amistad con estado 'pendiente'."""
    db_friendship = Friendship(
        user_1_id=user_1_id,
        user_2_id=user_2_id,
        action_user_id=action_user_id,
        status="pendiente"
    )
    db.add(db_friendship)
    db.commit()
    db.refresh(db_friendship)
    return db_friendship

def get_received_requests(db: Session, user_id: int) -> list[Friendship]:
    """Obtiene todas las solicitudes pendientes recibidas por un usuario."""
    statement = (
        select(Friendship)
        .where(
            or_(Friendship.user_1_id == user_id, Friendship.user_2_id == user_id),
            Friendship.status == "pendiente",
            Friendship.action_user_id != user_id # Donde yo no fui el último en actuar
        )
        .options(
            # Carga el 'user' que NO es el usuario actual (el solicitante)
            selectinload(Friendship.user1),
            selectinload(Friendship.user2)
        )
    )
    return db.exec(statement).all()

def get_friendship_by_id(db: Session, friendship_id: int) -> Friendship | None:
    """Obtiene una solicitud de amistad por su ID."""
    return db.get(Friendship, friendship_id)

def get_all_relations_map(db: Session, user_id: int) -> Dict[int, str]:
    """
    Devuelve un diccionario de todas las relaciones de un usuario
    (ID_del_otro_usuario: status).
    Esto es para filtrar la búsqueda de amigos.
    """
    statement = select(Friendship).where(
        or_(Friendship.user_1_id == user_id, Friendship.user_2_id == user_id)
    )
    relations = db.exec(statement).all()
    
    relations_map = {}
    for rel in relations:
        other_user_id = rel.user_2_id if rel.user_1_id == user_id else rel.user_1_id
        relations_map[other_user_id] = rel.status
    
    return relations_map

def save_friendship(db: Session, friendship: Friendship) -> Friendship:
    """Guarda (actualiza) un registro de amistad."""
    db.add(friendship)
    db.commit()
    db.refresh(friendship)
    return friendship

def delete_friendship(db: Session, friendship: Friendship):
    """Elimina un registro de amistad (para rechazar)."""
    db.delete(friendship)
    db.commit()
