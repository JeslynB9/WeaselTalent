from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime
from backend.db import SessionLocal
from backend.models import User

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Defines what frontend needs to send when creating a user
class UserCreate(BaseModel):
    email: str
    password: str
    role: str  # "candidate" | "recruiter" | "admin" etc.
    first_name: str
    last_name: str

class UserOut(BaseModel):
    user_id: int
    email: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# creates a group of routes under /users
router = APIRouter (
    prefix="/users",
    tags=["users"]
)

@router.post("/", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    fake_hash = f"hashed-{user.password}"

    db_user = User(
        email=user.email,
        password_hash = fake_hash,
        role=user.role,
        full_name=f"{user.first_name} {user.last_name}"
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

@router.get("/", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user