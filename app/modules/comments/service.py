from fastapi import Depends, HTTPException, status
from sqlmodel import Session

from app.db.session import get_db
from app.modules.users.model import User
from app.modules.posts.model import Post
from app.modules.comments import repository as comment_repository
from app.modules.comments.schemas import CommentCreate
from app.modules.comments.model import Comment


class CommentService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def create_comment(
        self,
        post_id: int,
        comment_in: CommentCreate,
        current_user: User
    ) -> Comment:
        """Crea un comentario en una publicación."""

        post = self.db.get(Post, post_id)
        if not post:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Publicación no encontrada.")

        return comment_repository.create_comment(
            db=self.db,
            content=comment_in.content,
            author_id=current_user.id,
            post_id=post_id
        )
