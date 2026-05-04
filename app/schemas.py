# APIの入出力
from pydantic import BaseModel


# ユーザー
class UserCreate(BaseModel):
    username: str
    password: str
    
    
class UserResponse(BaseModel):
    id: int
    username: str
    
    class Config:
        from_attributes = True
        

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
    content: str
    
    class Config:
        from_attributes = True