from sqlmodel import Session, select
from sqlalchemy.orm import selectinload, subqueryload
from typing import Optional

from app.modules.posts.model import Post
from app.modules.comments.model import Comment
from app.modules.users.model import User


def create_post(
    db: Session, 
    title: str, 
    description: str, 
    image_url: str | None, 
    author_id: int
) -> Post:
    """Crea un nuevo objeto Post y lo guarda en la BD."""
    
    db_post = Post(
        title=title,
        description=description,
        image_url=image_url,
        author_id=author_id
    )
    
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


def get_post_by_id(db: Session, post_id: int) -> Optional[Post]:
    """
    Obtiene un Post por su ID.
    
    Usa 'selectinload' y 'subqueryload' para cargar eficientemente
    (eager load) todas las relaciones necesarias para
    el schema 'PostReadWithComments' en una sola consulta.
    """
    statement = (
        select(Post)
        .where(Post.id == post_id)
        .options(
            selectinload(Post.author), 
            subqueryload(Post.comments).options(
                selectinload(Comment.author)
            )
        )
    )
    return db.exec(statement).first()


def save_post(db: Session, post_to_save: Post) -> Post:
    """Guarda (añade) un objeto Post ya modificado en la BD."""
    db.add(post_to_save)
    db.commit()
    db.refresh(post_to_save)
    return post_to_save