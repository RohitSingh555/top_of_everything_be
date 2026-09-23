import uuid
import re
import secrets
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, desc
from fastapi import HTTPException, status

from app.battles.models import Battle, BattleVote
from app.battles.schemas import (
    BattleCreateRequest, ChallengeCreateRequest, ChallengeAcceptRequest,
    BattleVoteRequest, BattlePublic, BattleHistoryItem, UserSummary
)
from app.users.models import User


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text[:45] or "battle"


def generate_unique_battle_slug(db: Session, title: str) -> str:
    base = slugify(title)
    for _ in range(10):
        random_suffix = secrets.token_hex(3)
        slug = f"{base}-{random_suffix}"
        if not db.query(Battle).filter(Battle.slug == slug).first():
            return slug
    return f"{base}-{uuid.uuid4().hex[:8]}"


def _build_user_summary(user: Optional[User]) -> Optional[UserSummary]:
    if not user:
        return None
    return UserSummary(
        id=user.id,
        username=user.username,
        display_name=user.profile.display_name if user.profile else None,
        avatar_url=user.profile.avatar_url if user.profile else None
    )


def to_public_battle(
    battle: Battle,
    user_vote: Optional[str] = None,
    has_voted: bool = False,
    requesting_user: Optional[User] = None
) -> BattlePublic:
    now = datetime.utcnow()
    reveal_at = battle.reveal_at

    # Determine if reveal time has passed
    can_reveal = (reveal_at is None) or (now >= reveal_at)

    # Hide tallies when results aren't yet revealed AND requester isn't the creator
    is_creator = requesting_user and battle.creator_id and str(requesting_user.id) == str(battle.creator_id)
    tallies_hidden = (not can_reveal) and (not is_creator)

    total = battle.total_votes
    if tallies_hidden:
        a_votes = 0
        b_votes = 0
        a_percent = 50.0
        b_percent = 50.0
        total_display = 0
    else:
        a_votes = battle.item_a_votes
        b_votes = battle.item_b_votes
        a_percent = round((a_votes / total * 100), 1) if total > 0 else 50.0
        b_percent = round((b_votes / total * 100), 1) if total > 0 else 50.0
        total_display = total

    return BattlePublic(
        id=battle.id,
        slug=battle.slug,
        title=battle.title,
        category=battle.category,
        battle_type=battle.battle_type,
        status=battle.status,
        creator=_build_user_summary(battle.creator),
        opponent=_build_user_summary(battle.opponent),
        opponent_name=battle.opponent_name,
        item_a_title=battle.item_a_title,
        item_a_image=battle.item_a_image,
        item_a_description=battle.item_a_description,
        item_a_ott=battle.item_a_ott,
        item_b_title=battle.item_b_title,
        item_b_image=battle.item_b_image,
        item_b_description=battle.item_b_description,
        item_b_ott=battle.item_b_ott,
        item_a_votes=a_votes,
        item_b_votes=b_votes,
        total_votes=total_display,
        item_a_percent=a_percent,
        item_b_percent=b_percent,
        has_voted=has_voted,
        user_vote=user_vote,
        winner_side=battle.winner_side if can_reveal else None,
        snapshot_data=battle.snapshot_data,
        reveal_at=reveal_at,
        can_reveal=can_reveal,
        tallies_hidden=tallies_hidden,
        created_at=battle.created_at
    )


# --- Create (Legacy instant battle / solo clash) ---

def create_battle(db: Session, user: Optional[User], data: BattleCreateRequest) -> BattlePublic:
    title = data.title.strip()
    if not title:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Battle title cannot be empty")

    opponent_id = None
    opponent_name = data.opponent_name.strip() if data.opponent_name else None
    if opponent_name:
        opp = db.query(User).filter(func.lower(User.username) == opponent_name.lower()).first()
        if opp:
            opponent_id = opp.id

    slug = generate_unique_battle_slug(db, title)
    status_val = "completed" if data.battle_type == "solo_clash" else "active"

    battle = Battle(
        slug=slug,
        title=title,
        category=data.category or "Movies",
        battle_type=data.battle_type or "user_challenge",
        status=status_val,
        creator_id=user.id if user else None,
        opponent_id=opponent_id,
        opponent_name=opponent_name,
        item_a_title=data.item_a_title.strip(),
        item_a_image=data.item_a_image,
        item_a_description=data.item_a_description,
        item_a_ott=data.item_a_ott,
        item_a_ranking_id=data.item_a_ranking_id,
        item_b_title=data.item_b_title.strip(),
        item_b_image=data.item_b_image,
        item_b_description=data.item_b_description,
        item_b_ott=data.item_b_ott,
        item_b_ranking_id=data.item_b_ranking_id,
        snapshot_data=data.snapshot_data
    )

    db.add(battle)
    db.commit()
    db.refresh(battle)
    return to_public_battle(battle, requesting_user=user)


# --- Create Challenge (Two-phase flow) ---

def create_challenge(db: Session, user: User, data: ChallengeCreateRequest) -> BattlePublic:
    title = data.title.strip()
    if not title:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Challenge title cannot be empty")

    opponent_name = data.opponent_name.strip()
    opp = db.query(User).filter(func.lower(User.username) == opponent_name.lower()).first()
    opponent_id = opp.id if opp else None

    if opp and str(opp.id) == str(user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You can't challenge yourself")

    slug = generate_unique_battle_slug(db, title)

    battle = Battle(
        slug=slug,
        title=title,
        category=data.category or "Movies",
        battle_type="user_challenge",
        status="pending_acceptance",
        creator_id=user.id,
        opponent_id=opponent_id,
        opponent_name=opponent_name,
        item_a_title=data.item_a_title.strip(),
        item_a_image=data.item_a_image,
        item_a_description=data.item_a_description,
        item_a_ott=data.item_a_ott,
        item_a_ranking_id=data.item_a_ranking_id,
        reveal_at=data.reveal_at
    )

    db.add(battle)
    db.commit()
    db.refresh(battle)
    return to_public_battle(battle, requesting_user=user)


# --- Accept Challenge ---

def accept_challenge(db: Session, user: User, slug: str, data: ChallengeAcceptRequest) -> BattlePublic:
    battle = db.query(Battle).filter(Battle.slug == slug).first()
    if not battle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")

    if battle.status != "pending_acceptance":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This challenge is not pending acceptance")

    if battle.opponent_id and str(battle.opponent_id) != str(user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the challenged user can accept this challenge")

    battle.item_b_title = data.item_b_title.strip()
    battle.item_b_image = data.item_b_image
    battle.item_b_description = data.item_b_description
    battle.item_b_ott = data.item_b_ott
    battle.item_b_ranking_id = data.item_b_ranking_id
    battle.opponent_id = user.id
    battle.opponent_name = user.username
    battle.status = "voting"
    battle.opponent_list_submitted_at = datetime.utcnow()

    db.commit()
    db.refresh(battle)
    return to_public_battle(battle, requesting_user=user)


# --- Decline Challenge ---

def decline_challenge(db: Session, user: User, slug: str) -> dict:
    battle = db.query(Battle).filter(Battle.slug == slug).first()
    if not battle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")

    if battle.status != "pending_acceptance":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This challenge cannot be declined")

    if battle.opponent_id and str(battle.opponent_id) != str(user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the challenged user can decline")

    battle.status = "declined"
    db.commit()
    return {"message": "Challenge declined"}


# --- Pending Challenges (Inbox) ---

def get_pending_challenges(db: Session, user: User) -> List[BattlePublic]:
    battles = db.query(Battle).filter(
        or_(
            Battle.opponent_id == user.id,
            func.lower(Battle.opponent_name) == user.username.lower()
        ),
        Battle.status == "pending_acceptance"
    ).order_by(desc(Battle.created_at)).all()

    return [to_public_battle(b, requesting_user=user) for b in battles]


# --- Get Battle by Slug ---

def get_battle_by_slug(
    db: Session, slug: str,
    user: Optional[User] = None,
    guest_id: Optional[str] = None
) -> BattlePublic:
    battle = db.query(Battle).filter(Battle.slug == slug).first()
    if not battle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Battle not found")

    has_voted = False
    user_vote = None

    if user:
        vote = db.query(BattleVote).filter(
            BattleVote.battle_id == battle.id,
            BattleVote.voter_id == user.id
        ).first()
        if vote:
            has_voted = True
            user_vote = vote.choice
    elif guest_id:
        vote = db.query(BattleVote).filter(
            BattleVote.battle_id == battle.id,
            BattleVote.guest_id == guest_id
        ).first()
        if vote:
            has_voted = True
            user_vote = vote.choice

    return to_public_battle(battle, user_vote=user_vote, has_voted=has_voted, requesting_user=user)


# --- Cast Vote ---

def cast_battle_vote(db: Session, slug: str, data: BattleVoteRequest, user: Optional[User] = None) -> BattlePublic:
    battle = db.query(Battle).filter(Battle.slug == slug).first()
    if not battle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Battle not found")

    if battle.status not in ("active", "voting"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Voting is not open for this battle")

    if user:
        existing = db.query(BattleVote).filter(
            BattleVote.battle_id == battle.id,
            BattleVote.voter_id == user.id
        ).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have already voted in this battle")
    elif data.guest_id:
        existing = db.query(BattleVote).filter(
            BattleVote.battle_id == battle.id,
            BattleVote.guest_id == data.guest_id
        ).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have already voted in this battle as a guest")
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Guest token or user authentication required to vote")

    voter_name = user.username if user else (data.voter_name or "Guest")

    vote = BattleVote(
        battle_id=battle.id,
        voter_id=user.id if user else None,
        guest_id=data.guest_id if not user else None,
        voter_name=voter_name,
        choice=data.choice
    )
    db.add(vote)

    if data.choice == "A":
        battle.item_a_votes += 1
    else:
        battle.item_b_votes += 1
    battle.total_votes += 1

    if battle.item_a_votes > battle.item_b_votes:
        battle.winner_side = "A"
    elif battle.item_b_votes > battle.item_a_votes:
        battle.winner_side = "B"
    else:
        battle.winner_side = "TIE"

    db.commit()
    db.refresh(battle)
    return to_public_battle(battle, user_vote=data.choice, has_voted=True, requesting_user=user)


# --- List Active Battles ---

def list_active_battles(db: Session, category: Optional[str] = None, limit: int = 20, offset: int = 0) -> List[BattlePublic]:
    query = db.query(Battle).filter(Battle.battle_type != "solo_clash", Battle.status.in_(["active", "voting"]))
    if category and category.lower() != "all":
        query = query.filter(func.lower(Battle.category) == category.lower())

    battles = query.order_by(desc(Battle.created_at)).offset(offset).limit(limit).all()
    return [to_public_battle(b) for b in battles]


# --- User Battle History ---

def get_user_battle_history(db: Session, user: User, limit: int = 50) -> List[BattleHistoryItem]:
    user_battles = db.query(Battle).filter(
        or_(
            Battle.creator_id == user.id,
            Battle.opponent_id == user.id
        )
    ).all()

    voted_rows = db.query(BattleVote).filter(BattleVote.voter_id == user.id).all()
    voted_battle_ids = {v.battle_id: v.choice for v in voted_rows}

    voted_battles = []
    if voted_battle_ids:
        voted_battles = db.query(Battle).filter(Battle.id.in_(list(voted_battle_ids.keys()))).all()

    seen = {}
    for b in user_battles:
        seen[b.id] = b
    for b in voted_battles:
        if b.id not in seen:
            seen[b.id] = b

    all_battles = sorted(seen.values(), key=lambda b: b.created_at, reverse=True)[:limit]

    now = datetime.utcnow()
    results: List[BattleHistoryItem] = []
    for b in all_battles:
        if b.battle_type == "solo_clash":
            role = "player"
        elif b.creator_id == user.id:
            role = "creator"
        elif b.opponent_id == user.id:
            role = "opponent"
        else:
            role = "voter"

        can_reveal = (b.reveal_at is None) or (now >= b.reveal_at)
        is_creator = str(b.creator_id) == str(user.id)
        tallies_visible = can_reveal or is_creator

        winner_title = None
        if tallies_visible:
            if b.winner_side == "A":
                winner_title = b.item_a_title
            elif b.winner_side == "B":
                winner_title = b.item_b_title
            elif b.snapshot_data and "champion" in b.snapshot_data:
                winner_title = b.snapshot_data["champion"]

        a_percent = round((b.item_a_votes / b.total_votes * 100), 1) if tallies_visible and b.total_votes > 0 else 50.0
        b_percent = round((b.item_b_votes / b.total_votes * 100), 1) if tallies_visible and b.total_votes > 0 else 50.0

        results.append(
            BattleHistoryItem(
                id=b.id,
                slug=b.slug,
                title=b.title,
                category=b.category,
                battle_type=b.battle_type,
                status=b.status,
                role=role,
                winner_title=winner_title,
                item_a_title=b.item_a_title,
                item_a_image=b.item_a_image,
                item_b_title=b.item_b_title,
                item_b_image=b.item_b_image,
                item_a_votes=b.item_a_votes if tallies_visible else 0,
                item_b_votes=b.item_b_votes if tallies_visible else 0,
                total_votes=b.total_votes if tallies_visible else 0,
                item_a_percent=a_percent,
                item_b_percent=b_percent,
                user_choice=voted_battle_ids.get(b.id),
                reveal_at=b.reveal_at,
                can_reveal=can_reveal,
                created_at=b.created_at
            )
        )

    return results
