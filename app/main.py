from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func

from app import models, schemas, auth
from app.database import SessionLocal, engine


models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SNS API",
    description="FastAPIで作成したSNSバックエンドAPI",
    version="1.0.0"
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# DBセッション取得
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ユーザー登録
@app.post("/users", response_model=schemas.UserResponse, tags=["Users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed_pw = auth.hash_password(user.password)

    db_user = models.User(
        username=user.username,
        password=hashed_pw
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# ログイン
@app.post("/login", response_model=schemas.Token, tags=["Auth"])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()

    if not user or not auth.verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = auth.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


# 現在のユーザー取得
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = auth.decode_token(token)

    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user


# 投稿作成
@app.post("/posts", response_model=schemas.PostResponse, tags=["Posts"])
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
@app.get("/posts", response_model=list[schemas.PostResponse], tags=["Posts"])
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


# いいね追加
@app.post("/posts/{post_id}/like", tags=["Likes"])
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
@app.delete("/posts/{post_id}/like", tags=["Likes"])
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


# フォロー一覧
@app.get("/users/me/following", response_model=schemas.UserListResponse, tags=["Follows"])
def get_following(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    follows = db.query(models.Follow).filter(
        models.Follow.follower_id == current_user.id
    ).all()

    users = [follow.following_user for follow in follows]
    return {"users": users}


# フォロワー一覧
@app.get("/users/me/followers", response_model=schemas.UserListResponse, tags=["Follows"])
def get_followers(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    follows = db.query(models.Follow).filter(
        models.Follow.following_id == current_user.id
    ).all()

    users = [follow.follower for follow in follows]
    return {"users": users}


# フォロー
@app.post("/users/{user_id}/follow", tags=["Follows"])
def follow_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")

    target_user = db.query(models.User).filter(models.User.id == user_id).first()

    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    follow = models.Follow(
        follower_id=current_user.id,
        following_id=user_id
    )

    try:
        db.add(follow)
        db.commit()
    except:
        db.rollback()
        raise HTTPException(status_code=400, detail="Already following")

    return {"message": "Followed"}


# アンフォロー
@app.delete("/users/{user_id}/follow", tags=["Follows"])
def unfollow_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    follow = db.query(models.Follow).filter(
        models.Follow.follower_id == current_user.id,
        models.Follow.following_id == user_id
    ).first()

    if not follow:
        raise HTTPException(status_code=404, detail="Follow not found")

    db.delete(follow)
    db.commit()
    return {"message": "Unfollowed"}