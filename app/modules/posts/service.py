from fastapi import Depends, HTTPException, status, UploadFile
from sqlmodel import Session
import os
import shutil
from uuid import uuid4

from app.db.session import get_db
from app.modules.users.model import User
from . import repository as post_repository
from .model import Post

POST_IMAGE_DIR = "/data/avatars" 
POST_IMAGE_URL_DIR = "/static/avatars"

os.makedirs(POST_IMAGE_DIR, exist_ok=True)

MAX_POST_IMAGE_SIZE_MB = 2
MAX_POST_IMAGE_SIZE_BYTES = MAX_POST_IMAGE_SIZE_MB * 1024 * 1024
ALLOWED_POST_MIMETYPE = "image/jpeg"

class PostService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def _save_post_image(self, file: UploadFile, user_id: int) -> str:
        """
        Valida y guarda una imagen. Devuelve la URL pública.
        """

        if file.content_type != ALLOWED_POST_MIMETYPE:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, 
                detail=f"Formato de imagen no válido. Solo se permite {ALLOWED_POST_MIMETYPE} (JPG)."
            )

        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0) 
        if file_size > MAX_POST_IMAGE_SIZE_BYTES:
            raise HTTPException(
                status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"La imagen es demasiado grande. Límite: {MAX_POST_IMAGE_SIZE_MB}MB."
            )

        file_name = f"post_{user_id}_{uuid4()}.jpg"
        file_path_on_disk = os.path.join(POST_IMAGE_DIR, file_name)
        file_url_path = f"{POST_IMAGE_URL_DIR}/{file_name}"

        try:
            with open(file_path_on_disk, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Error al guardar la imagen: {e}")
        
        return file_url_path
    
    def _delete_post_image(self, image_url: str | None):
        """Borra una imagen del volumen."""
        if not image_url:
            return
        try:
            filename = image_url.split('/')[-1]
            path_on_disk = os.path.join(POST_IMAGE_DIR, filename)
            if os.path.exists(path_on_disk):
                os.remove(path_on_disk)
        except Exception as e:
            print(f"Error al borrar imagen antigua: {e}")

    def create_post(
        self, 
        title: str, 
        description: str, 
        file: UploadFile, 
        current_user: User
    ) -> Post:
        """Crea una nueva publicación."""
        
        if not current_user.is_superuser:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "No tienes permisos para crear publicaciones.")
            
        image_url = self._save_post_image(file, current_user.id)
    
        return post_repository.create_post(
            db=self.db,
            title=title,
            description=description,
            image_url=image_url,
            author_id=current_user.id
        )

    def get_post(self, post_id: int) -> Post:
        """Obtiene una publicación por ID (con comentarios)."""
        post = post_repository.get_post_by_id(self.db, post_id)
        if not post:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Publicación no encontrada.")
        return post

    def update_post(
        self,
        post_id: int,
        description: str | None,
        file: UploadFile | None,
        current_user: User
    ) -> Post:
        """Actualiza la descripción y/o imagen de una publicación."""
        
        # 1. Permiso
        if not current_user.is_superuser:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "No tienes permisos para modificar esta publicación.")
            
        # 2. Obtener el post (sin comentarios, más rápido)
        post = self.db.get(Post, post_id)
        if not post:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Publicación no encontrada.")

        # 3. Actualizar campos (Regla de Negocio)
        if description is not None:
            post.description = description
            
        if file is not None:
            # Borra la imagen antigua
            self._delete_post_image(post.image_url)
            # Guarda la nueva y actualiza la URL
            post.image_url = self._save_post_image(file, current_user.id)
            
        # 4. Guardar cambios
        return post_repository.save_post(self.db, post)
