from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.auth.router import router as auth_router
from app.users.router import router as users_router
from app.entities.router import router as entities_router
from app.rankings.router import router as rankings_router

from app.database import engine, Base
import app.users.models  # Import models to ensure they are registered with Base
import app.entities.models
import app.rankings.models

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

@app.get("/health")
def health_check():
    return {"status": "ok", "environment": settings.ENVIRONMENT}

@app.get("/")
def root():
    return {"message": "Welcome to Rankr API. Visit /docs for OpenAPI documentation."}
