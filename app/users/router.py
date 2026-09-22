from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.users.schemas import UserPublicProfile, ProfileUpdateRequest
from app.users.service import get_user_profile, update_user_profile, follow_user, unfollow_user
from app.common.dependencies import get_current_user
from app.users.models import User

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserPublicProfile)
def get_my_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_user_profile(db, current_user.username)

@router.patch("/me", response_model=UserPublicProfile)
def update_my_profile(data: ProfileUpdateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return update_user_profile(db, current_user, data)

@router.get("/{username}", response_model=UserPublicProfile)
def get_profile(username: str, db: Session = Depends(get_db)):
    return get_user_profile(db, username)

@router.post("/{username}/follow", status_code=status.HTTP_200_OK)
def follow(username: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return follow_user(db, current_user, username)

@router.delete("/{username}/follow", status_code=status.HTTP_200_OK)
def unfollow(username: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return unfollow_user(db, current_user, username)
