from sqlalchemy.orm import Session
from typing import Optional
from fastapi import HTTPException, status
from app.users.models import User, Profile, Follow
from app.users.schemas import ProfileUpdateRequest

def get_user_profile(db: Session, username: str, viewer: Optional[User] = None) -> dict:
    user = db.query(User).filter(User.username == username).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    profile = user.profile
    if not profile:
        profile = Profile(user_id=user.id, display_name=user.username)
        db.add(profile)
        db.commit()

    # Relationship of the viewing user to this profile (if authenticated)
    is_self = bool(viewer and viewer.id == user.id)
    is_following = False
    if viewer and not is_self:
        is_following = db.query(Follow).filter(
            Follow.follower_id == viewer.id,
            Follow.following_id == user.id
        ).first() is not None

    return {
        "username": user.username,
        "display_name": profile.display_name or user.username,
        "avatar_url": profile.avatar_url,
        "bio": profile.bio,
        "website": profile.website,
        "follower_count": profile.follower_count,
        "following_count": profile.following_count,
        "ranking_count": profile.ranking_count,
        "is_following": is_following,
        "is_self": is_self,
        "created_at": user.created_at
    }

def update_user_profile(db: Session, user: User, data: ProfileUpdateRequest) -> dict:
    profile = user.profile
    if not profile:
        profile = Profile(user_id=user.id, display_name=user.username)
        db.add(profile)

    if data.display_name is not None:
        profile.display_name = data.display_name
    if data.bio is not None:
        profile.bio = data.bio
    if data.website is not None:
        profile.website = data.website
    if data.avatar_url is not None:
        profile.avatar_url = data.avatar_url

    db.commit()
    return get_user_profile(db, user.username, viewer=user)

def follow_user(db: Session, current_user: User, target_username: str):
    target = db.query(User).filter(User.username == target_username).first()
    if not target or not target.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User to follow not found")
    
    if target.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot follow yourself")

    existing = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.following_id == target.id
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already following this user")

    follow = Follow(follower_id=current_user.id, following_id=target.id)
    db.add(follow)

    # Update counts
    target_profile = target.profile
    if target_profile:
        target_profile.follower_count += 1
    
    current_profile = current_user.profile
    if current_profile:
        current_profile.following_count += 1

    db.commit()
    return {"message": f"Successfully followed @{target_username}"}

def unfollow_user(db: Session, current_user: User, target_username: str):
    target = db.query(User).filter(User.username == target_username).first()
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    existing = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.following_id == target.id
    ).first()
    if not existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not following this user")

    db.delete(existing)

    # Update counts
    target_profile = target.profile
    if target_profile and target_profile.follower_count > 0:
        target_profile.follower_count -= 1
    
    current_profile = current_user.profile
    if current_profile and current_profile.following_count > 0:
        current_profile.following_count -= 1

    db.commit()
    return {"message": f"Successfully unfollowed @{target_username}"}
