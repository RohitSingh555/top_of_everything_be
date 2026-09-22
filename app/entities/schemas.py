from pydantic import BaseModel
from typing import Optional, List, Any
from uuid import UUID
from datetime import datetime

class EntityBase(BaseModel):
    name: str
    type: str
    aliases: Optional[List[str]] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    metadata_json: Optional[Any] = None
    external_ids: Optional[Any] = None

class EntityCreate(EntityBase):
    pass

class EntityPublic(EntityBase):
    id: UUID
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True
