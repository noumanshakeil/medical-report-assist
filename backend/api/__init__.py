from fastapi import APIRouter
from backend.api import health, medical, ui
api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(medical.router, prefix="/api", tags=["medical"])
api_router.include_router(ui.router, tags=["ui"])
