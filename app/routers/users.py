from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas, auth
from app.database import SessionLocal


router = APIRouter(tags=["Users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
# ユーザー登録
@router.post("/users", response_model=schemas.UserResponse, tags=["Users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed = auth.hash_password(user.password)

    db_user = models.User(
        username=user.username,
        password=hashed
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user