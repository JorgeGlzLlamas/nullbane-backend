from sqlmodel import Session
from app.modules.comments.model import Comment
from app.modules.comments.schemas import CommentCreate

def create_comment(
    db: Session, 
    content: str, 
    author_id: int, 
    post_id: int
) -> Comment:
    """Crea un nuevo comentario y lo guarda en la BD."""
    
    db_comment = Comment(
        content=content,
        author_id=author_id,
        post_id=post_id
    )
    
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment
