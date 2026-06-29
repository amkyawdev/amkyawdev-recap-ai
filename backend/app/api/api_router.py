"""
API Router
"""
from fastapi import APIRouter
from app.api.endpoints import recap, voice, video_edit, render, export, upload, hybrid

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(recap.router, prefix="/recap", tags=["recap"])
api_router.include_router(voice.router, prefix="/voice", tags=["voice"])
api_router.include_router(video_edit.router, prefix="/video", tags=["video"])
api_router.include_router(render.router, prefix="/render", tags=["render"])
api_router.include_router(export.router, prefix="/export", tags=["export"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(hybrid.router, prefix="/hybrid", tags=["hybrid"])
