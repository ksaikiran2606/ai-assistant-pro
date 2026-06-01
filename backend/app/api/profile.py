"""User profile and dashboard API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas import ChatResponse, ProfileResponse, UserResponse
from app.services import chat_service

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("", response_model=ProfileResponse)
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stats = chat_service.get_user_stats(db, current_user)
    recent = [
        ChatResponse(
            id=c.id,
            user_id=c.user_id,
            title=c.title,
            created_at=c.created_at,
            message_count=chat_service.get_message_count_for_chat(db, c.id),
        )
        for c in stats["recent_chats"]
    ]
    return ProfileResponse(
        user=UserResponse.model_validate(current_user),
        total_chats=stats["total_chats"],
        total_messages=stats["total_messages"],
        recent_chats=recent,
    )
