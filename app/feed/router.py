from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.common.dependencies import get_current_user
from app.feed.service import get_following_feed
from app.rankings.schemas import RankingPublic
from app.users.models import User

router = APIRouter(prefix="/feed", tags=["Feed"])


@router.get("", response_model=List[RankingPublic])
def get_feed(
    category: Optional[str] = None,
    q: Optional[str] = None,
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Paginated feed of published rankings from users the current user follows."""
    return get_following_feed(
        db, current_user, category=category, q=q, limit=limit, offset=offset
    )
