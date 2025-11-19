from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from sqlalchemy import or_, desc, asc
import datetime

from app.modules.friendships.model import Friendship
from .model import Message

def get_active_chats_for_user(db: Session, user_id: int, search: str | None) -> list[Friendship]:
    """
    Obtiene todos los chats 'aceptados' de un usuario,
    ordenados por el último mensaje.
    """
    statement = (
        select(Friendship)
        .where(
            or_(Friendship.user_1_id == user_id, Friendship.user_2_id == user_id),
            Friendship.status == "aceptada"
        )
        .options(
            # Carga ambos lados de la relación
            selectinload(Friendship.user1), 
            selectinload(Friendship.user2),
            # Carga el último mensaje
            selectinload(Friendship.messages)
        )
    )
    
    # Ordena por la marca de tiempo del chat
    statement = statement.order_by(desc(Friendship.last_message_at))
    
    results = db.exec(statement).all()
    
    # Filtro de búsqueda en Python (después de la consulta)
    if search:
        search_lower = search.lower()
        filtered_results = []
        for chat in results:
            other_user = chat.user1 if chat.user1.id != user_id else chat.user2
            full_name = f"{other_user.first_name} {other_user.last_name or ''}".lower()
            if search_lower in full_name or search_lower in other_user.username.lower():
                filtered_results.append(chat)
        return filtered_results
        
    return results

def get_messages_for_chat(
    db: Session, 
    friendship_id: int, 
    limit: int = 50, 
    offset: int = 0
) -> list[Message]:
    """Obtiene los mensajes de un chat, paginados y ordenados del más nuevo al más viejo."""
    statement = (
        select(Message)
        .where(Message.friendship_id == friendship_id)
        .order_by(desc(Message.created_at)) # El frontend los invertirá
        .limit(limit)
        .offset(offset)
    )
    return db.exec(statement).all()

def create_message(
    db: Session, 
    content: str, 
    friendship_id: int, 
    sender_id: int
) -> Message:
    """Crea un nuevo mensaje y actualiza el 'last_message_at' del chat."""
    
    # 1. Obtiene el chat (Friendship)
    db_friendship = db.get(Friendship, friendship_id)
    if not db_friendship:
        return None # El servicio manejará el 404
        
    # 2. Crea el mensaje
    db_message = Message(
        content=content,
        friendship_id=friendship_id,
        sender_id=sender_id
    )
    
    # 3. Actualiza la marca de tiempo del chat (Regla 2)
    db_friendship.last_message_at = datetime.datetime.now(datetime.timezone.utc)
    
    db.add(db_message)
    db.add(db_friendship) # Añade ambos para la transacción
    
    db.commit()
    
    db.refresh(db_message)
    return db_message
