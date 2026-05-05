from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models
from app.database import SessionLocal
from app.dependencies import get_current_user


router = APIRouter(tags=["Likes"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        

# いいね追加
@router.post("/posts/{post_id}/like", summary="いいね追加")
def like_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    like = models.Like(user_id=current_user.id, post_id=post_id)

    try:
        db.add(like)
        db.commit()
    except:
        db.rollback()
        raise HTTPException(status_code=400, detail="Already liked")

    return {"message": "Liked"}


# いいね削除
@router.delete("/posts/{post_id}/like", summary="いいね削除")
def unlike_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    like = db.query(models.Like).filter(
        models.Like.user_id == current_user.id,
        models.Like.post_id == post_id
    ).first()

    if not like:
        raise HTTPException(status_code=404, detail="Like not found")

    db.delete(like)
    db.commit()
    return {"message": "Unliked"}