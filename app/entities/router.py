from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from app.database import get_db
from app.entities.schemas import EntityPublic, EntityCreate
from app.entities.service import search_entities, create_entity, get_entity_by_id
from app.common.dependencies import get_current_user
from app.users.models import User

router = APIRouter(prefix="/entities", tags=["Entities"])

@router.get("/search", response_model=List[EntityPublic])
def search(
    q: Optional[str] = Query(None, description="Search query string"),
    type: Optional[str] = Query(None, description="Filter by entity type (movie, game, pokemon, etc)"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return search_entities(db, query=q, entity_type=type, limit=limit)

@router.post("", response_model=EntityPublic, status_code=status.HTTP_201_CREATED)
def create(data: EntityCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return create_entity(db, data, current_user)

@router.get("/{entity_id}", response_model=EntityPublic)
def get_one(entity_id: UUID, db: Session = Depends(get_db)):
    return get_entity_by_id(db, entity_id)
