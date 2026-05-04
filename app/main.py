from fastapi import FastAPI
from app import models
from app.database import engine
from app.routers import auth, users, posts, likes, follows


models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SNS API",
    description="FastAPIで作成したSNSバックエンドAPI",
    version="1.0.0"
)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(likes.router)
app.include_router(follows.router)