from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.entities.schemas import EntityPublic

class ItemInput(BaseModel):
    entity_id: Optional[UUID] = None
    custom_name: Optional[str] = None
    custom_image_url: Optional[str] = None
    position: int = Field(..., ge=1)
    note: Optional[str] = Field(None, max_length=1000)

class RankingCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    category: Optional[str] = "other"
    size: int = Field(10, ge=3, le=100)
    visibility: str = "public"  # public | unlisted | followers | private
    type: str = "standard"
    items: Optional[List[ItemInput]] = []

class RankingUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    category: Optional[str] = None
    visibility: Optional[str] = None
    size: Optional[int] = Field(None, ge=3, le=100)

class RankingItemPublic(BaseModel):
    id: UUID
    position: int
    entity_id: Optional[UUID] = None
    custom_name: Optional[str] = None
    custom_image_url: Optional[str] = None
    note: Optional[str] = None
    entity: Optional[EntityPublic] = None

    class Config:
        from_attributes = True

class UserMinimal(BaseModel):
    id: UUID
    username: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True

class RankingPublic(BaseModel):
    id: UUID
    slug: str
    title: str
    description: Optional[str] = None
    type: str
    category: Optional[str] = None
    size: int
    visibility: str
    status: str
    view_count: int
    like_count: int
    comment_count: int
    created_at: datetime
    published_at: Optional[datetime] = None
    user: Optional[UserMinimal] = None
    items: List[RankingItemPublic] = []

    class Config:
        from_attributes = True

class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)
    parent_id: Optional[UUID] = None

class CommentPublic(BaseModel):
    id: UUID
    ranking_id: UUID
    user_id: UUID
    content: str
    parent_id: Optional[UUID] = None
    created_at: datetime
    user: Optional[UserMinimal] = None

    class Config:
        from_attributes = True
