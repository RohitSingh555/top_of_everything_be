from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.rankings.models import Ranking
from app.users.models import Follow, User


def get_following_feed(
    db: Session,
    user: User,
    category: Optional[str] = None,
    q: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
) -> List[Ranking]:
    """Published rankings created by users that `user` follows."""
    following_ids = [
        row[0]
        for row in db.query(Follow.following_id).filter(Follow.follower_id == user.id).all()
    ]
    if not following_ids:
        return []

    query = db.query(Ranking).filter(
        Ranking.user_id.in_(following_ids),
        Ranking.status == "published",
        Ranking.visibility.in_(["public", "followers"]),
    )

    if category and category.lower() != "all":
        query = query.filter(Ranking.category.ilike(category))

    if q and q.strip():
        search_term = f"%{q.strip()}%"
        query = query.filter(
            Ranking.title.ilike(search_term) | Ranking.description.ilike(search_term)
        )

    return (
        query.order_by(func.coalesce(Ranking.published_at, Ranking.created_at).desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
