"""Chat management API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas import ChatCreate, ChatListResponse, ChatResponse, ChatUpdate
from app.services import chat_service

router = APIRouter(prefix="/chats", tags=["Chats"])


def _chat_to_response(db: Session, chat) -> ChatResponse:
    return ChatResponse(
        id=chat.id,
        user_id=chat.user_id,
        title=chat.title,
        created_at=chat.created_at,
        message_count=chat_service.get_message_count_for_chat(db, chat.id),
    )


@router.get("", response_model=ChatListResponse)
def list_chats(
    search: str | None = Query(None, description="Search chats by title"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    chats = chat_service.get_user_chats(db, current_user.id, search)
    return ChatListResponse(
        chats=[_chat_to_response(db, c) for c in chats],
        total=len(chats),
    )


@router.post("", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
def create_chat(
    data: ChatCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    chat = chat_service.create_chat(db, current_user.id, data.title or "New Chat")
    return _chat_to_response(db, chat)


@router.patch("/{chat_id}", response_model=ChatResponse)
def rename_chat(
    chat_id: int,
    data: ChatUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    chat = chat_service.get_chat(db, chat_id, current_user.id)
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    chat = chat_service.update_chat_title(db, chat, data.title)
    return _chat_to_response(db, chat)


@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    chat = chat_service.get_chat(db, chat_id, current_user.id)
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    chat_service.delete_chat(db, chat)
    return None
