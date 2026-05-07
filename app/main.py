from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models
from app.database import Base, engine
from app.routers import auth, users, posts, likes, follows


models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SNS API",
    description="FastAPIで作成したSNSバックエンドAPI",
    version="1.0.0"
)

# CORS
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=[""],
    allow_headers=["*"]
)

# routers
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(likes.router)
app.include_router(follows.router)