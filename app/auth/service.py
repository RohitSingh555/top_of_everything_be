from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.users.models import User, Profile
from app.auth.schemas import RegisterRequest, LoginRequest, TokenResponse
from app.auth.utils import hash_password, verify_password, create_access_token, create_refresh_token, decode_token

def register_user(db: Session, data: RegisterRequest) -> TokenResponse:
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")

    user = User(
        email=data.email,
        username=data.username,
        password_hash=hash_password(data.password)
    )
    db.add(user)
    db.flush()

    profile = Profile(
        user_id=user.id,
        display_name=data.username
    )
    db.add(profile)
    db.commit()
    db.refresh(user)

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

def login_user(db: Session, data: LoginRequest) -> TokenResponse:
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not user.password_hash or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

def refresh_user_tokens(refresh_token: str) -> TokenResponse:
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        user_id = payload.get("sub")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    access_token = create_access_token({"sub": user_id})
    new_refresh_token = create_refresh_token({"sub": user_id})
    return TokenResponse(access_token=access_token, refresh_token=new_refresh_token)
