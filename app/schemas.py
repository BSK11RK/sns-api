# APIの入出力
from pydantic import BaseModel
from datetime import datetime


# ユーザー
class UserCreate(BaseModel):
    username: str
    password: str
    
    
class UserResponse(BaseModel):
    id: int
    username: str
    
    class Config:
        from_attributes = True
        
        
class UserListResponse(BaseModel):
    users: list[UserResponse]
        

# Auth
class Token(BaseModel):
    access_token: str
    token_type: str


# 投稿
class PostCreate(BaseModel):
    content: str
    
    
class PostResponse(BaseModel):
    id: int
    user: UserResponse
    created_at: datetime
    content: str
    likes_count: int
    
    class Config:
        from_attributes = True