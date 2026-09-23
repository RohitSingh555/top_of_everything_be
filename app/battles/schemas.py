from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

class UserSummary(BaseModel):
    id: UUID
    username: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True

# ─── Creation Schemas ──────────────────────────────────────────────────────────

class BattleCreateRequest(BaseModel):
    """Legacy: instant battle where both items are known at creation."""
    title: str = Field(..., min_length=2, max_length=255)
    category: str = Field(default="Movies", max_length=50)
    battle_type: str = Field(default="user_challenge")
    opponent_name: Optional[str] = None

    item_a_title: str = Field(..., min_length=1, max_length=255)
    item_a_image: Optional[str] = None
    item_a_description: Optional[str] = None
    item_a_ott: Optional[List[str]] = None
    item_a_ranking_id: Optional[UUID] = None

    item_b_title: str = Field(..., min_length=1, max_length=255)
    item_b_image: Optional[str] = None
    item_b_description: Optional[str] = None
    item_b_ott: Optional[List[str]] = None
    item_b_ranking_id: Optional[UUID] = None

    snapshot_data: Optional[Dict[str, Any]] = None

class ChallengeCreateRequest(BaseModel):
    """Challenge flow: Creator sets topic + their own list, tags opponent, sets reveal time."""
    title: str = Field(..., min_length=2, max_length=255)
    category: str = Field(default="Movies", max_length=50)
    opponent_name: str = Field(..., min_length=1, max_length=100)  # target opponent's username

    # Creator's list/pick (Option A)
    item_a_title: str = Field(..., min_length=1, max_length=255)
    item_a_image: Optional[str] = None
    item_a_description: Optional[str] = None
    item_a_ott: Optional[List[str]] = None
    item_a_ranking_id: Optional[UUID] = None

    # Reveal time — when results will be shown to everyone
    reveal_at: Optional[datetime] = None

class ChallengeAcceptRequest(BaseModel):
    """Opponent accepts the challenge and submits their own list (Option B)."""
    item_b_title: str = Field(..., min_length=1, max_length=255)
    item_b_image: Optional[str] = None
    item_b_description: Optional[str] = None
    item_b_ott: Optional[List[str]] = None
    item_b_ranking_id: Optional[UUID] = None

# ─── Vote Schema ───────────────────────────────────────────────────────────────

class BattleVoteRequest(BaseModel):
    choice: str = Field(..., pattern="^(A|B)$")
    guest_id: Optional[str] = None
    voter_name: Optional[str] = None

# ─── Response Schemas ──────────────────────────────────────────────────────────

class BattlePublic(BaseModel):
    id: UUID
    slug: str
    title: str
    category: str
    battle_type: str
    status: str
    creator: Optional[UserSummary] = None
    opponent: Optional[UserSummary] = None
    opponent_name: Optional[str] = None

    item_a_title: str
    item_a_image: Optional[str] = None
    item_a_description: Optional[str] = None
    item_a_ott: Optional[List[str]] = None

    item_b_title: Optional[str] = None   # nullable until opponent submits
    item_b_image: Optional[str] = None
    item_b_description: Optional[str] = None
    item_b_ott: Optional[List[str]] = None

    item_a_votes: int = 0
    item_b_votes: int = 0
    total_votes: int = 0
    item_a_percent: float = 0.0
    item_b_percent: float = 0.0

    has_voted: bool = False
    user_vote: Optional[str] = None
    winner_side: Optional[str] = None
    snapshot_data: Optional[Dict[str, Any]] = None

    reveal_at: Optional[datetime] = None
    can_reveal: bool = True  # False if reveal_at is in the future
    tallies_hidden: bool = False  # True if votes are hidden pending reveal

    created_at: datetime

    class Config:
        from_attributes = True

class BattleHistoryItem(BaseModel):
    id: UUID
    slug: str
    title: str
    category: str
    battle_type: str
    status: str
    role: str  # "creator" | "opponent" | "voter" | "player"
    winner_title: Optional[str] = None
    item_a_title: str
    item_a_image: Optional[str] = None
    item_b_title: Optional[str] = None
    item_b_image: Optional[str] = None
    item_a_votes: int = 0
    item_b_votes: int = 0
    total_votes: int = 0
    item_a_percent: float = 0.0
    item_b_percent: float = 0.0
    user_choice: Optional[str] = None
    reveal_at: Optional[datetime] = None
    can_reveal: bool = True
    created_at: datetime

    class Config:
        from_attributes = True

