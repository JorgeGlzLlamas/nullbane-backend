from fastapi import Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from app.db.session import get_db
from app.modules.users.model import User
from app.modules.users.schemas import UserSearchRead, AuthorRead
from app.modules.users import repository as user_repository
from . import repository as friendship_repository
from .schemas import FriendRequestRead
from .model import Friendship

class FriendshipService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def search_potential_friends(
        self, 
        current_user: User, 
        name_query: str
    ) -> list[UserSearchRead]:
        """
        Servicio para la barra de búsqueda de 'Agregar Amigos'.
        Filtra usuarios que no sean amigos, pendientes, o el propio usuario.
        """
        # 1. Llama al repositorio de usuarios para la búsqueda ILIKE
        found_users = user_repository.search_users_by_name_prefix(
            self.db, 
            search_query=name_query
        )
        
        # 2. Carga un mapa de todas tus relaciones actuales
        current_relations_map = friendship_repository.get_all_relations_map(
            self.db, user_id=current_user.id
        )
        
        # 3. Filtra la lista (tu lógica de negocio)
        valid_users_to_add = []
        for user in found_users:
            if user.id == current_user.id:
                continue # No te incluyas a ti mismo
            
            if user.id in current_relations_map:
                continue # Ya tienes una relación (amigo o pendiente)
            
            valid_users_to_add.append(user)

        # 4. Convierte al schema de respuesta
        return [UserSearchRead.model_validate(user) for user in valid_users_to_add]

    def get_received_requests(self, current_user: User) -> list[FriendRequestRead]:
        """Obtiene la lista de solicitudes de amistad recibidas."""
        requests = friendship_repository.get_received_requests(self.db, user_id=current_user.id)
        
        response = []
        for req in requests:
            # Determina quién es el solicitante
            requester_user = req.user1 if req.user1.id != current_user.id else req.user2
            response.append(
                FriendRequestRead(
                    id=req.id,
                    requester=AuthorRead.model_validate(requester_user)
                )
            )
        return response

    def send_friend_request(self, current_user: User, target_user_id: int) -> Friendship:
        """Envía una solicitud de amistad."""
        if current_user.id == target_user_id:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "No puedes enviarte una solicitud a ti mismo.")
        
        # Verifica si ya existe una relación
        existing = friendship_repository.get_friendship_by_users(
            self.db, current_user.id, target_user_id
        )
        if existing:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Ya existe una relación o solicitud con este usuario.")
            
        # Implementa la regla del ID más bajo/alto
        user_1_id = min(current_user.id, target_user_id)
        user_2_id = max(current_user.id, target_user_id)
        
        return friendship_repository.create_friend_request(
            db=self.db,
            user_1_id=user_1_id,
            user_2_id=user_2_id,
            action_user_id=current_user.id # Tú hiciste la acción
        )

    def _validate_friendship_action(self, friendship_id: int, current_user: User) -> Friendship:
        """Helper para validar Aceptar/Rechazar."""
        friendship = friendship_repository.get_friendship_by_id(self.db, friendship_id)
        
        if not friendship:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Solicitud no encontrada.")
        
        # Verifica que el usuario actual es el RECEPTOR de la solicitud
        is_recipient = (
            friendship.status == "pendiente" and
            friendship.action_user_id != current_user.id and
            (friendship.user_1_id == current_user.id or friendship.user_2_id == current_user.id)
        )
        
        if not is_recipient:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "No tienes permiso para realizar esta acción.")
            
        return friendship

    def accept_friend_request(self, friendship_id: int, current_user: User):
        """Acepta una solicitud de amistad."""
        friendship = self._validate_friendship_action(friendship_id, current_user)
        
        friendship.status = "aceptada"
        friendship.action_user_id = current_user.id # Tú aceptaste
        
        friendship_repository.save_friendship(self.db, friendship)
        return

    def reject_friend_request(self, friendship_id: int, current_user: User):
        """Rechaza (y borra) una solicitud de amistad."""
        friendship = self._validate_friendship_action(friendship_id, current_user)
        
        friendship_repository.delete_friendship(self.db, friendship)
        return
