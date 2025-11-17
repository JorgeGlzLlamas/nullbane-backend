from fastapi import Depends, HTTPException, status
from sqlmodel import Session

from app.db.session import get_db
from app.modules.users.model import User
from . import repository as achievement_repo
from .schemas import AchievementWithStatus, AchievementCreate, AchievementRead

class AchievementService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def get_catalog_with_status(self, current_user: User) -> list[AchievementWithStatus]:
        """
        Obtiene el catálogo completo de logros y marca cuáles 
        tiene desbloqueados el usuario actual.
        """
        # 1. Obtener TODO el catálogo de logros disponibles
        all_achievements = achievement_repo.get_all_achievements(self.db)
        
        # 2. Obtener SOLO los vínculos del usuario (sus logros ganados)
        user_links = achievement_repo.get_user_achievements(self.db, current_user.id)
        
        # 3. Crear un diccionario para búsqueda rápida (O(1))
        # Clave: achievement_id -> Valor: fecha de obtención (earned_at)
        # Esto evita hacer una búsqueda anidada lenta dentro del bucle
        earned_map = {link.achievement_id: link.created_at for link in user_links}
        
        # 4. Construir la respuesta fusionada
        results = []
        for achievement in all_achievements:
            # Verificamos si el ID del logro está en el mapa del usuario
            is_owned = achievement.id in earned_map
            
            results.append(AchievementWithStatus(
                id=achievement.id,
                name=achievement.name,
                description=achievement.description,
                # Campos enriquecidos:
                is_unlocked=is_owned,
                earned_at=earned_map.get(achievement.id) # Devuelve la fecha o None
            ))
            
        return results

    def unlock_achievement(self, user_id: int, achievement_id: int):
        """
        Lógica para otorgar un logro a un usuario.
        Verifica si el logro existe y si el usuario ya lo tiene para no duplicar.
        """
        # 1. Verificar que el logro existe en el catálogo
        achievement = achievement_repo.get_achievement_by_id(self.db, achievement_id)
        if not achievement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Logro no encontrado."
            )

        # 2. Verificar si el usuario ya tiene este logro
        existing_link = achievement_repo.get_user_achievement_link(self.db, user_id, achievement_id)
        if existing_link:
            # Ya lo tiene. Podemos lanzar error o simplemente retornar el existente.
            # Retornamos el existente para ser idempotentes (seguro de reintentar).
            return existing_link

        # 3. Otorgar el logro (crear el vínculo)
        return achievement_repo.add_achievement_to_user(self.db, user_id, achievement_id)
    
    def create_new_achievement(
        self, 
        current_user: User, 
        achievement_in: AchievementCreate
    ) -> AchievementRead:
        """
        Crea un nuevo logro.
        Solo permitido para Superusuarios.
        """
        
        # 1. Validar Permisos (Is Superuser?)
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para crear logros."
            )
            
        # 2. Validar Duplicados (Nombre único)
        if achievement_repo.get_achievement_by_name(self.db, achievement_in.name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un logro con este nombre."
            )
            
        # 3. Crear
        return achievement_repo.create_achievement(self.db, achievement_in)