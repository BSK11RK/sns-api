from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app import models, schemas
from app.database import SessionLocal
from app.dependencies import get_current_user


router = APIRouter(tags=["Posts"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
# 投稿作成
@router.post("/posts", response_model=schemas.PostResponse, tags=["Posts"])
def create_post(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_post = models.Post(
        content=post.content,
        user_id=current_user.id
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    return {
        **db_post.__dict__,
        "likes_count": 0
    }
    
    
# 投稿一覧
@router.get("/posts", response_model=list[schemas.PostResponse], tags=["Posts"])
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()

    result = []
    for post in posts:
        likes_count = db.query(func.count(models.Like.id))\
            .filter(models.Like.post_id == post.id)\
            .scalar()

        result.append({
            "id": post.id,
            "user": post.user,
            "content": post.content,
            "likes_count": likes_count
        })

    return result