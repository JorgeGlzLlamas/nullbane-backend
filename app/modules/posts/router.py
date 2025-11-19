from fastapi import APIRouter, Depends, status, Form, File, UploadFile
from sqlmodel import Session
from typing import Optional, Iterator, List

from app.db.session import get_db
from app.auth_security import get_current_user
from app.modules.users.model import User
from app.modules.posts.schemas import PostRead, PostReadWithComments
from app.modules.posts.service import PostService
from app.modules.comments.router import router as comments_router
from fastapi import Query

router = APIRouter()

@router.get(
    "/",
    response_model=List[PostRead],
    summary="Obtener feed de publicaciones"
)
def get_posts_feed(
    limit: int = Query(20, ge=1, le=100, description="Cantidad de posts a traer"),
    offset: int = Query(0, ge=0, description="Desde qué post empezar (paginación)"),
    service: PostService = Depends()
):
    """
    Devuelve una lista de las publicaciones más recientes.
    Incluye información del autor, pero no los comentarios.
    """
    return service.get_feed(limit=limit, offset=offset)

@router.post(
    "/",
    response_model=PostRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva publicación (Solo Superusuarios)"
)
def create_post(
    title: str = Form(..., description="Título del post"),
    description: str = Form(..., description="Descripción/contenido del post"),
    file: UploadFile = File(..., description="Imagen JPG (Max 2MB)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: PostService = Depends()
):
    """
    Crea una nueva publicación.
    - **Requiere permisos de Superusuario.**
    - Envía los datos como `multipart/form-data`.
    """
    return service.create_post(
        title=title,
        description=description,
        file=file,
        current_user=current_user
    )

@router.get(
    "/{post_id}",
    response_model=PostReadWithComments,
    summary="Ver detalles de una publicación"
)
def get_post_details(
    post_id: int,
    db: Session = Depends(get_db),
    service: PostService = Depends()
):
    """
    Obtiene la información completa de una publicación,
    incluyendo su autor y la lista de comentarios (con sus autores).
    """
    return service.get_post(post_id=post_id)

@router.put(
    "/{post_id}",
    response_model=PostRead,
    summary="Actualizar una publicación (Solo Superusuarios)"
)
def update_post_details(
    post_id: int,
    description: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None, description="Nueva imagen JPG (Max 2MB)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: PostService = Depends()
):
    """
    Actualiza la descripción y/o la imagen de una publicación.
    - **Requiere permisos de Superusuario.**
    - El título no se puede modificar.
    - Envía los datos como `multipart/form-data`.
    """
    return service.update_post(
        post_id=post_id,
        description=description,
        file=file,
        current_user=current_user
    )

router.include_router(
    comments_router,
    prefix="/{post_id}/comments",
    tags=["Comentarios"]
)