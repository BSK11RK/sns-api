from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import SessionLocal
from app.dependencies import get_current_user


router = APIRouter(tags=["Follows"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# フォロー一覧
@router.get("/users/me/following", response_model=schemas.UserListResponse)
def following(
    db: Session = Depends(get_db), 
    me: models.User = Depends(get_current_user)
):
    follows = db.query(models.Follow).filter(
        models.Follow.follower_id == me.id
    ).all()
    return {"users": [f.following_user for f in follows]}


# フォロワー一覧
@router.get("/users/me/followers", response_model=schemas.UserListResponse)
def followers(
    db: Session = Depends(get_db), 
    me: models.User = Depends(get_current_user)
):
    follows = db.query(models.Follow).filter(
        models.Follow.following_id == me.id
    ).all()
    return {"users": [f.follower for f in follows]}
       
        
# フォロー
@router.post("/users/{user_id}/follow")
def follow(
    user_id: int, 
    db: Session = Depends(get_db), 
    me: models.User = Depends(get_current_user)
):
    if user_id == me.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")

    follow = models.Follow(follower_id=me.id, following_id=user_id)

    try:
        db.add(follow)
        db.commit()
    except:
        db.rollback()
        raise HTTPException(status_code=400, detail="Already following")

    return {"message": "Followed"}


# アンフォロー
@router.delete("/users/{user_id}/follow")
def unfollow(
    user_id: int, 
    db: Session = Depends(get_db), 
    me: models.User = Depends(get_current_user)
):
    follow = db.query(models.Follow).filter(
        models.Follow.follower_id == me.id,
        models.Follow.following_id == user_id
    ).first()

    if not follow:
        raise HTTPException(status_code=404, detail="Not found")

    db.delete(follow)
    db.commit()

    return {"message": "Unfollowed"}