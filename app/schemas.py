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
    
    
class PostUpdate(BaseModel):
    content: str
    
    
class PostResponse(BaseModel):
    id: int
    content: str
    created_at: datetime
    user: UserResponse
    likes_count: int
    
    class Config:
        from_attributes = True