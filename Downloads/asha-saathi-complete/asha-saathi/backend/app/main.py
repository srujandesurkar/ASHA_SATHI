"""
ASHA Saathi - Main FastAPI Application
======================================
AI Voice Field Register for ASHA Workers
PS1 · Healthcare Hackathon Solution
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db, AsyncSessionLocal
from app.services.synthetic_data_loader import seed_synthetic_data
from app.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables
    await init_db()
    # Seed realistic synthetic beneficiaries and follow-ups
    async with AsyncSessionLocal() as session:
        await seed_synthetic_data(session)
    yield


app = FastAPI(
    title="ASHA Saathi – AI Voice Field Register for ASHA Workers",
    description="Multilingual voice agent for Indic and English code-mixed maternal & newborn healthcare visit recording.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API endpoints under /api
app.include_router(api_router, prefix="/api")


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ASHA Saathi Backend",
        "gnani_live_api": settings.is_gnani_configured,
        "mode": "Live Gnani API" if settings.is_gnani_configured else "Gnani Demo Mode (Active)",
        "ai_disclosure_enabled": settings.DISCLOSE_AI_IDENTITY
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
