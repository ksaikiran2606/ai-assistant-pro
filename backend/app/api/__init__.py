"""API router aggregation."""

from fastapi import APIRouter

from app.api import auth, chats, messages, profile

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(chats.router)
api_router.include_router(messages.router)
api_router.include_router(profile.router)
