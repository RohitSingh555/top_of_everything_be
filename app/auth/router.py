from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.schemas import RegisterRequest, LoginRequest, TokenResponse, RefreshRequest, UserResponse
from app.auth.service import register_user, login_user, refresh_user_tokens
from app.common.dependencies import get_current_user
from app.users.models import User

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    return register_user(db, data)

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    return login_user(db, data)

@router.post("/refresh", response_model=TokenResponse)
def refresh(data: RefreshRequest):
    return refresh_user_tokens(data.refresh_token)

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
