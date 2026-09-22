import uuid
import re
import secrets
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status
from typing import Optional, List
from app.rankings.models import Ranking, RankingItem, RankingVersion, Like, Comment
from app.rankings.schemas import RankingCreateRequest, RankingUpdateRequest, ItemInput, CommentCreate
from app.users.models import User, Follow

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text[:40] or "ranking"

def generate_unique_slug(db: Session, title: str) -> str:
    base = slugify(title)
    for _ in range(10):
        random_suffix = secrets.token_hex(3)
        slug = f"{base}-{random_suffix}"
        if not db.query(Ranking).filter(Ranking.slug == slug).first():
            return slug
    return f"{base}-{uuid.uuid4().hex[:8]}"

def create_ranking(db: Session, user: User, data: RankingCreateRequest) -> Ranking:
    slug = generate_unique_slug(db, data.title)
    ranking = Ranking(
        slug=slug,
        user_id=user.id,
        title=data.title,
        description=data.description,
        category=data.category,
        size=data.size,
        visibility=data.visibility,
        type=data.type,
        status="published"
    )
    db.add(ranking)
    db.flush()

    if data.items:
        positions_seen = set()
        for item_data in data.items:
            if item_data.position in positions_seen:
                continue
            positions_seen.add(item_data.position)
            
            item = RankingItem(
                ranking_id=ranking.id,
                entity_id=item_data.entity_id,
                custom_name=item_data.custom_name,
                custom_image_url=item_data.custom_image_url,
                position=item_data.position,
                note=item_data.note
            )
            db.add(item)

    if user.profile:
        user.profile.ranking_count += 1

    ranking.published_at = datetime.utcnow()
    db.commit()
    db.refresh(ranking)
    return ranking

def get_ranking_by_slug(db: Session, slug: str, viewer: Optional[User] = None) -> Ranking:
    ranking = db.query(Ranking).filter(Ranking.slug == slug).first()
    if not ranking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ranking not found")

    # Visibility checks
    if ranking.visibility == "private":
        if not viewer or viewer.id != ranking.user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This ranking is private")
    elif ranking.visibility == "followers":
        if not viewer:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This ranking is for followers only")
        if viewer.id != ranking.user_id:
            is_following = db.query(Follow).filter(
                Follow.follower_id == viewer.id,
                Follow.following_id == ranking.user_id
            ).first()
            if not is_following:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only followers can view this ranking")

    # Increment views
    ranking.view_count += 1
    db.commit()
    db.refresh(ranking)
    return ranking

def update_ranking(db: Session, slug: str, user: User, data: RankingUpdateRequest) -> Ranking:
    ranking = db.query(Ranking).filter(Ranking.slug == slug).first()
    if not ranking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ranking not found")
    if ranking.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to edit this ranking")

    if data.title is not None:
        ranking.title = data.title
    if data.description is not None:
        ranking.description = data.description
    if data.category is not None:
        ranking.category = data.category
    if data.visibility is not None:
        ranking.visibility = data.visibility
    if data.size is not None:
        ranking.size = data.size

    db.commit()
    db.refresh(ranking)
    return ranking

def delete_ranking(db: Session, slug: str, user: User):
    ranking = db.query(Ranking).filter(Ranking.slug == slug).first()
    if not ranking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ranking not found")
    if ranking.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this ranking")

    if user.profile and user.profile.ranking_count > 0:
        user.profile.ranking_count -= 1

    db.delete(ranking)
    db.commit()
    return {"message": "Ranking deleted successfully"}

def toggle_like(db: Session, slug: str, user: User):
    ranking = db.query(Ranking).filter(Ranking.slug == slug).first()
    if not ranking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ranking not found")

    existing = db.query(Like).filter(Like.ranking_id == ranking.id, Like.user_id == user.id).first()
    if existing:
        db.delete(existing)
        if ranking.like_count > 0:
            ranking.like_count -= 1
        liked = False
    else:
        like = Like(ranking_id=ranking.id, user_id=user.id)
        db.add(like)
        ranking.like_count += 1
        liked = True

    db.commit()
    return {"liked": liked, "like_count": ranking.like_count}

def add_comment(db: Session, slug: str, user: User, data: CommentCreate) -> Comment:
    ranking = db.query(Ranking).filter(Ranking.slug == slug).first()
    if not ranking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ranking not found")

    comment = Comment(
        ranking_id=ranking.id,
        user_id=user.id,
        content=data.content,
        parent_id=data.parent_id
    )
    db.add(comment)
    ranking.comment_count += 1
    db.commit()
    db.refresh(comment)
    return comment

def get_comments(db: Session, slug: str) -> List[Comment]:
    ranking = db.query(Ranking).filter(Ranking.slug == slug).first()
    if not ranking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ranking not found")
    return db.query(Comment).filter(Comment.ranking_id == ranking.id).order_by(Comment.created_at.asc()).all()
