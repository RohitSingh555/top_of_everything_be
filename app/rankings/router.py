from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.rankings.schemas import (
    RankingCreateRequest, RankingUpdateRequest, RankingPublic,
    CommentCreate, CommentPublic
)
from app.rankings.service import (
    create_ranking, get_ranking_by_slug, update_ranking, delete_ranking,
    toggle_like, add_comment, get_comments
)
from app.common.dependencies import get_current_user, get_optional_user
from app.users.models import User

router = APIRouter(prefix="/rankings", tags=["Rankings"])

@router.post("", response_model=RankingPublic, status_code=status.HTTP_201_CREATED)
def create(data: RankingCreateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return create_ranking(db, current_user, data)

@router.get("/{slug}", response_model=RankingPublic)
def get_one(slug: str, optional_user: Optional[User] = Depends(get_optional_user), db: Session = Depends(get_db)):
    return get_ranking_by_slug(db, slug, optional_user)

@router.patch("/{slug}", response_model=RankingPublic)
def update(slug: str, data: RankingUpdateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return update_ranking(db, slug, current_user, data)

@router.delete("/{slug}", status_code=status.HTTP_200_OK)
def delete(slug: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return delete_ranking(db, slug, current_user)

@router.post("/{slug}/like", status_code=status.HTTP_200_OK)
def like(slug: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return toggle_like(db, slug, current_user)

@router.post("/{slug}/comments", response_model=CommentPublic, status_code=status.HTTP_201_CREATED)
def post_comment(slug: str, data: CommentCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return add_comment(db, slug, current_user, data)

@router.get("/{slug}/comments", response_model=List[CommentPublic])
def list_comments(slug: str, db: Session = Depends(get_db)):
    return get_comments(db, slug)
