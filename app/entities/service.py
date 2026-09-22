from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status
from typing import Optional, List
from uuid import UUID
from app.entities.models import Entity
from app.entities.schemas import EntityCreate
from app.users.models import User

def search_entities(db: Session, query: Optional[str] = None, entity_type: Optional[str] = None, limit: int = 20) -> List[Entity]:
    q = db.query(Entity)
    if entity_type:
        q = q.filter(Entity.type == entity_type)
    
    if query:
        search_pattern = f"%{query}%"
        q = q.filter(
            or_(
                Entity.name.ilike(search_pattern),
                Entity.aliases.any(query)
            )
        )
    return q.limit(limit).all()

def create_entity(db: Session, data: EntityCreate, user: Optional[User] = None) -> Entity:
    entity = Entity(
        name=data.name,
        type=data.type,
        aliases=data.aliases,
        image_url=data.image_url,
        description=data.description,
        metadata_json=data.metadata_json,
        external_ids=data.external_ids,
        is_verified=False,
        created_by=user.id if user else None
    )
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity

def get_entity_by_id(db: Session, entity_id: UUID) -> Entity:
    entity = db.query(Entity).filter(Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
    return entity
