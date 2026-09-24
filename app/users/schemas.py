from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class UserPublicProfile(BaseModel):
    username: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    website: Optional[str] = None
    follower_count: int = 0
    following_count: int = 0
    ranking_count: int = 0
    is_following: bool = False
    is_self: bool = False
    created_at: datetime

    class Config:
        from_attributes = True

class ProfileUpdateRequest(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    website: Optional[str] = None
    avatar_url: Optional[str] = None
