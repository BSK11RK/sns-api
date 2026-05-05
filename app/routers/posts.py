from fastapi import APIRouter, Depends, Query, HTTPException
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
@router.post("/posts", response_model=schemas.PostResponse)
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
    
    
# 投稿更新
@router.put("/posts/{post_id}", response_model=schemas.PostResponse)
def update_post(
    post_id: int,
    post: schemas.PostUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # 自分の投稿かチェック
    if db_post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db_post.content = post.content
    
    db.commit()
    db.refresh(db_post)
    
    likes = db.query(func.count(models.Like.id)).filter(
        models.Like.post_id == db_post.id
    ).scalar()
    
    return {
        "id": db_post.id,
        "content": db_post.content,
        "created_at": db_post.created_at,
        "user": db_post.user,
        "likes_count": likes
    }


# 投稿削除
@router.delete("/posts/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # 自分の投稿かチェック
    if db_post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db.delete(db_post)
    db.commit()
    return {"message": "Deleted"}
    
    
# 投稿一覧（ページネーション対応）
@router.get("/posts", response_model=list[schemas.PostResponse])
def get_posts(
    db: Session = Depends(get_db),
    limit: int = Query(10, le=100),
    offset: int = Query(0, ge=0)
):
    posts = db.query(models.Post) \
        .order_by(models.Post.created_at.desc()) \
        .limit(limit).offset(offset).all()

    result = []
    for post in posts:
        likes_count = db.query(func.count(models.Like.id))\
            .filter(models.Like.post_id == post.id)\
            .scalar()

        result.append({
            "id": post.id,
            "user": post.user,
            "content": post.content,
            "created_at": post.created_at,
            "likes_count": likes_count
        })
    return result


# タイムライン（ページネーション対応）
@router.get("/timeline", response_model=list[schemas.PostResponse])
def get_timeline(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    limit: int = Query(10, le=100),
    offset: int = Query(0, ge=0)
):
    # フォローしているユーザーID取得
    follows = db.query(models.Follow).filter(
        models.Follow.follower_id == current_user.id
    ).all()
    
    following_ids = [f.following_id for f in follows]
    
    # 自分も含める
    following_ids.append(current_user.id)
    
    # 投稿取得（新しい順）
    posts = db.query(models.Post) \
        .filter(models.Post.user_id.in_(following_ids)) \
        .order_by(models.Post.created_at.desc()) \
        .limit(limit).offset(offset).all()
    
    # いいね数付きで返す
    result = []
    for post in posts:
        likes = db.query(func.count(models.Like.id)).filter(
            models.Like.post_id == post.id
        ).scalar()
        
        result.append({
            "id": post.id,
            "content": post.content,
            "created_at": post.created_at,  
            "user": post.user,
            "likes_count": likes
        })
    return result