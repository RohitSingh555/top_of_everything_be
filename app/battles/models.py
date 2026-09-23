import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base

class Battle(Base):
    __tablename__ = "battles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False, default="Movies", index=True)
    battle_type = Column(String(50), nullable=False, default="user_challenge")
    # Status flow:
    #   "pending_acceptance"   → challenge sent, opponent hasn't accepted yet
    #   "voting"               → both lists submitted, voting is live
    #   "completed"            → solo_clash auto-logged or manually closed
    #   "declined"             → opponent declined the challenge
    #   "active"               → legacy / simple user_challenge (instant)
    status = Column(String(30), nullable=False, default="active")

    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    opponent_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    opponent_name = Column(String(100), nullable=True)

    # Option A — Creator's list/pick
    item_a_title = Column(String(255), nullable=False)
    item_a_image = Column(Text, nullable=True)
    item_a_description = Column(Text, nullable=True)
    item_a_ott = Column(JSONB, nullable=True)
    item_a_ranking_id = Column(UUID(as_uuid=True), ForeignKey("rankings.id", ondelete="SET NULL"), nullable=True)

    # Option B — Opponent's list/pick (nullable until opponent accepts the challenge)
    item_b_title = Column(String(255), nullable=True)
    item_b_image = Column(Text, nullable=True)
    item_b_description = Column(Text, nullable=True)
    item_b_ott = Column(JSONB, nullable=True)
    item_b_ranking_id = Column(UUID(as_uuid=True), ForeignKey("rankings.id", ondelete="SET NULL"), nullable=True)

    # Vote tallies
    item_a_votes = Column(Integer, nullable=False, default=0)
    item_b_votes = Column(Integer, nullable=False, default=0)
    total_votes = Column(Integer, nullable=False, default=0)
    winner_side = Column(String(10), nullable=True)  # "A" | "B" | "TIE"

    # Reveal time — results (vote tallies) are hidden until this datetime
    reveal_at = Column(DateTime, nullable=True)

    # Additional metadata (e.g. for solo gauntlet snapshots)
    snapshot_data = Column(JSONB, nullable=True)

    # Timestamps
    opponent_list_submitted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    creator = relationship("User", foreign_keys=[creator_id], backref="created_battles")
    opponent = relationship("User", foreign_keys=[opponent_id], backref="challenged_battles")
    votes = relationship("BattleVote", back_populates="battle", cascade="all, delete-orphan")


class BattleVote(Base):
    __tablename__ = "battle_votes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    battle_id = Column(UUID(as_uuid=True), ForeignKey("battles.id", ondelete="CASCADE"), nullable=False, index=True)
    voter_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    guest_id = Column(String(128), nullable=True, index=True)
    voter_name = Column(String(100), nullable=True)
    choice = Column(String(10), nullable=False)  # "A" | "B"
    created_at = Column(DateTime, default=datetime.utcnow)

    battle = relationship("Battle", back_populates="votes")
    voter = relationship("User", foreign_keys=[voter_id], backref="battle_votes")

    __table_args__ = (
        Index("uq_battle_vote_user", "battle_id", "voter_id", unique=True, postgresql_where=(voter_id.is_not(None))),
        Index("uq_battle_vote_guest", "battle_id", "guest_id", unique=True, postgresql_where=(guest_id.is_not(None))),
    )
