from passlib.context import CryptContext
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional

from backend.db import SessionLocal
from backend.models import User, UserProfile

router = APIRouter(prefix="/auth", tags=["auth"])

# --------------------
# DB Dependency
# --------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --------------------
# Password utils
# --------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    # bcrypt max is 72 bytes
    # password_bytes = password.encode("utf-8")[:72]
    # return pwd_context.hash(password_bytes)
    return password

def verify_password(plain: str, hashed: str) -> bool:
    # password_bytes = plain.encode("utf-8")[:72]
    # return pwd_context.verify(password_bytes, hashed)
    return plain

# --------------------
# Schemas
# --------------------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    role: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class SignupResponse(BaseModel):
    id: int
    email: EmailStr
    role: str


# --------------------
# Routes
# --------------------
@router.post("/signup", response_model=SignupResponse)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=request.email,
        password_hash=hash_password(request.password),
        role=request.role
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    if request.first_name or request.last_name:
        full_name = " ".join(
            part for part in [request.first_name, request.last_name] if part
        )
        db.add(UserProfile(user_id=user.user_id, name=full_name))
        db.commit()

    return {
        "id": user.user_id,
        "email": user.email,
        "role": user.role
    }


@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    return {
        "id": user.user_id,
        "role": user.role
    }
