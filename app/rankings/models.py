import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base

class Ranking(Base):
    __tablename__ = "rankings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(2000), nullable=True)
    type = Column(String(50), default="standard")  # standard | blind | battle | community
    category = Column(String(50), nullable=True, index=True)  # movies | games | books | music | food | tech | sports | anime | other
    size = Column(Integer, nullable=False, default=10)  # 3-100
    visibility = Column(String(20), default="public")  # public | unlisted | followers | private
    status = Column(String(20), default="draft")  # draft | published
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)

    user = relationship("User", backref="rankings")
    items = relationship("RankingItem", back_populates="ranking", order_by="RankingItem.position", cascade="all, delete-orphan")
    versions = relationship("RankingVersion", back_populates="ranking", cascade="all, delete-orphan")


class RankingItem(Base):
    __tablename__ = "ranking_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ranking_id = Column(UUID(as_uuid=True), ForeignKey("rankings.id", ondelete="CASCADE"), nullable=False, index=True)
    entity_id = Column(UUID(as_uuid=True), ForeignKey("entities.id", ondelete="SET NULL"), nullable=True)
    custom_name = Column(String(255), nullable=True)
    custom_image_url = Column(Text, nullable=True)
    position = Column(Integer, nullable=False)  # 1-indexed
    note = Column(String(1000), nullable=True)  # The "Why?" text
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    ranking = relationship("Ranking", back_populates="items")
    entity = relationship("Entity")

    __table_args__ = (
        UniqueConstraint("ranking_id", "position", name="uq_ranking_item_position"),
    )


class RankingVersion(Base):
    __tablename__ = "ranking_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ranking_id = Column(UUID(as_uuid=True), ForeignKey("rankings.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    snapshot = Column(JSONB, nullable=False)
    change_summary = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    ranking = relationship("Ranking", back_populates="versions")


class Like(Base):
    __tablename__ = "likes"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    ranking_id = Column(UUID(as_uuid=True), ForeignKey("rankings.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Comment(Base):
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ranking_id = Column(UUID(as_uuid=True), ForeignKey("rankings.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(String(1000), nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("comments.id", ondelete="CASCADE"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User")
