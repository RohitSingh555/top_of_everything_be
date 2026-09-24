from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import settings
from app.auth.router import router as auth_router
from app.users.router import router as users_router
from app.entities.router import router as entities_router
from app.rankings.router import router as rankings_router
from app.battles.router import router as battles_router
from app.feed.router import router as feed_router

from app.database import engine, Base, get_db
import app.users.models
import app.entities.models
import app.rankings.models
import app.battles.models

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Rankr API",
    description="Social Ranking Platform Backend API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(entities_router)
app.include_router(rankings_router)
app.include_router(battles_router)
app.include_router(feed_router)


@app.get("/health")
def health_check():
    return {"status": "ok", "environment": settings.ENVIRONMENT}


@app.get("/stats")
def platform_stats(db: Session = Depends(get_db)):
    """Public platform statistics — used by the footer."""
    from app.users.models import User
    from app.rankings.models import Ranking
    from app.battles.models import Battle
    total_users    = db.query(func.count(User.id)).scalar() or 0
    total_rankings = db.query(func.count(Ranking.id)).scalar() or 0
    total_battles  = db.query(func.count(Battle.id)).scalar() or 0
    total_votes    = db.query(func.sum(Battle.total_votes)).scalar() or 0
    return {
        "total_users":    total_users,
        "total_rankings": total_rankings,
        "total_battles":  total_battles,
        "total_votes":    int(total_votes),
    }


@app.get("/")
def root():
    return {"message": "Welcome to Rankr API. Visit /docs for OpenAPI documentation."}
