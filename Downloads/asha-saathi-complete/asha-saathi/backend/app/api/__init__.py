from fastapi import APIRouter
from app.api.beneficiaries import router as beneficiaries_router
from app.api.visits import router as visits_router
from app.api.voice import router as voice_router
from app.api.danger_signs import router as danger_signs_router
from app.api.follow_ups import router as follow_ups_router
from app.api.dashboard import router as dashboard_router

api_router = APIRouter()
api_router.include_router(voice_router)
api_router.include_router(visits_router)
api_router.include_router(danger_signs_router)
api_router.include_router(beneficiaries_router)
api_router.include_router(follow_ups_router)
api_router.include_router(dashboard_router)
