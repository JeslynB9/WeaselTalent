from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db import SessionLocal
from models import User, Recruiter

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

class LoginIn(BaseModel):
    email: str
    password: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login")
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user or user.password_hash != f"hashed-{payload.password}":
        raise HTTPException(status_code=401, detail="Invalid credentials")
    out = {
        "user_id": user.user_id,
        "email": user.email,
        "role": user.role,
        "full_name": user.full_name,
    }

    # If user is a recruiter, also return the linked recruiter_id (if exists)
    if user.role == "recruiter":
        rec = db.query(Recruiter).filter(Recruiter.user_id == user.user_id).first()
        if rec:
            out["recruiter_id"] = rec.recruiter_id

    return out
