# APIの入出力
from pydantic import BaseModel, Field
from datetime import datetime


# ユーザー
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    password: str = Field(..., min_length=6, max_length=100)
    
    
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
    content: str = Field(..., min_length=1, max_length=200)
    
    
class PostUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=200)
    
    
class PostResponse(BaseModel):
    id: int
    content: str
    created_at: datetime
    user: UserResponse
    likes_count: int
    
    class Config:
        from_attributes = True