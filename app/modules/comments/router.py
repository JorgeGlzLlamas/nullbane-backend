from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from typing import Iterator

from app.db.session import get_db
from app.auth_security import get_current_user
from app.modules.users.model import User
from app.modules.comments.schemas import CommentCreate, CommentRead
from app.modules.comments.service import CommentService


router = APIRouter()

@router.post(
    "/",
    response_model=CommentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo comentario"
)
def create_comment_on_post(
    post_id: int, 
    comment_in: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: CommentService = Depends()
):
    """
    Crea un nuevo comentario en una publicación específica.
    Cualquier usuario autenticado puede comentar.
    """
    return service.create_comment(
        post_id=post_id,
        comment_in=comment_in,
        current_user=current_user
    )