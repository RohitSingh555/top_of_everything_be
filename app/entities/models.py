import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from app.database import Base

class Entity(Base):
    __tablename__ = "entities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    type = Column(String(50), nullable=False, index=True)  # e.g. "movie", "game", "book", "person", "place", "product", "music", "pokemon", "other"
    aliases = Column(ARRAY(String), nullable=True)
    image_url = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    metadata_json = Column("metadata", JSONB, nullable=True)
    external_ids = Column(JSONB, nullable=True)
    is_verified = Column(Boolean, default=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_entities_name_type", "name", "type"),
    )
