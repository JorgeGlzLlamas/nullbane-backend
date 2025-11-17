from fastapi import Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from app.db.session import get_db
from app.modules.users.model import User
from app.modules.users.schemas import AuthorRead
from app.modules.friendships.model import Friendship
from . import repository as chat_repository
from .schemas import ChatListRead, MessageRead, MessageCreate
from .model import Message

class ChatService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def get_chat_list(self, current_user: User, search: str | None) -> list[ChatListRead]:
        """Servicio para la Lista de Chats (Pantalla 1)."""
        
        chats = chat_repository.get_active_chats_for_user(self.db, current_user.id, search)
        
        response_list = []
        for chat in chats:
            # Determina quién es el "otro" usuario
            other_user_obj = chat.user1 if chat.user1.id != current_user.id else chat.user2
            
            last_message_content = None
            if chat.messages:
                # La consulta de 'messages' no está optimizada para 
                # obtener solo el último, así que lo hacemos en Python
                # (Esto es lento, pero funciona para empezar)
                last_message_content = chat.messages[-1].content
            
            chat_item = ChatListRead(
                friendship_id=chat.id,
                other_user=AuthorRead.model_validate(other_user_obj),
                last_message_content=last_message_content,
                last_message_at=chat.last_message_at
            )
            response_list.append(chat_item)
            
        return response_list

    def _get_valid_chat(self, friendship_id: int, user_id: int) -> Friendship:
        """Helper que valida si el usuario pertenece a este chat 'aceptado'."""
        chat = self.db.get(Friendship, friendship_id)
        
        if not chat:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Chat no encontrado.")
            
        if chat.status != "aceptada":
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Esta amistad no está aceptada.")
            
        if user_id not in (chat.user_1_id, chat.user_2_id):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "No perteneces a este chat.")
            
        return chat

    def get_messages(self, friendship_id: int, current_user: User) -> list[MessageRead]:
        """Servicio para obtener mensajes (Pantalla 2)."""
        # Valida que el usuario tenga acceso a este chat
        self._get_valid_chat(friendship_id, current_user.id)
        
        messages = chat_repository.get_messages_for_chat(self.db, friendship_id)
        # Los mensajes vienen del más nuevo al más viejo, los invertimos
        return [MessageRead.model_validate(msg) for msg in reversed(messages)]

    def send_message(
        self, 
        friendship_id: int, 
        message_in: MessageCreate, 
        current_user: User
    ) -> MessageRead:
        """Servicio para enviar un mensaje (Pantalla 2)."""
        # Valida que el usuario tenga acceso a este chat
        self._get_valid_chat(friendship_id, current_user.id)
        
        message = chat_repository.create_message(
            db=self.db,
            content=message_in.content,
            friendship_id=friendship_id,
            sender_id=current_user.id
        )
        
        return MessageRead.model_validate(message)