from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.common.dependencies import get_current_user, get_optional_user
from app.users.models import User
from app.battles.schemas import (
    BattleCreateRequest, ChallengeCreateRequest, ChallengeAcceptRequest,
    BattleVoteRequest, BattlePublic, BattleHistoryItem
)
from app.battles.service import (
    create_battle, create_challenge, accept_challenge, decline_challenge,
    get_pending_challenges, get_battle_by_slug, cast_battle_vote,
    list_active_battles, get_user_battle_history
)

router = APIRouter(prefix="/battles", tags=["Battles"])


# --- Public ---

@router.get("", response_model=List[BattlePublic])
def list_battles(
    category: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    return list_active_battles(db, category=category, limit=limit, offset=offset)


# --- Legacy instant battle / solo clash ---

@router.post("", response_model=BattlePublic, status_code=status.HTTP_201_CREATED)
def create(
    data: BattleCreateRequest,
    optional_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    return create_battle(db, optional_user, data)


# --- Challenge (Two-phase flow) ---

@router.post("/challenge", response_model=BattlePublic, status_code=status.HTTP_201_CREATED)
def create_new_challenge(
    data: ChallengeCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a challenge — sets topic + creator's list, waits for opponent to accept."""
    return create_challenge(db, current_user, data)


@router.get("/challenges/pending", response_model=List[BattlePublic])
def pending_challenges(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all incoming challenges pending acceptance for the current user."""
    return get_pending_challenges(db, current_user)


# --- History ---

@router.get("/history/me", response_model=List[BattleHistoryItem])
def history(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_user_battle_history(db, current_user, limit=limit)


# --- Individual Battle ---

@router.get("/{slug}", response_model=BattlePublic)
def get_one(
    slug: str,
    guest_id: Optional[str] = Query(None),
    optional_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    return get_battle_by_slug(db, slug, optional_user, guest_id=guest_id)


@router.post("/{slug}/accept", response_model=BattlePublic)
def accept(
    slug: str,
    data: ChallengeAcceptRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Opponent accepts the challenge and submits their list — activates voting."""
    return accept_challenge(db, current_user, slug, data)


@router.post("/{slug}/decline", status_code=status.HTTP_200_OK)
def decline(
    slug: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Opponent declines the challenge."""
    return decline_challenge(db, current_user, slug)


@router.post("/{slug}/vote", response_model=BattlePublic)
def vote(
    slug: str,
    data: BattleVoteRequest,
    optional_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    return cast_battle_vote(db, slug, data, optional_user)
