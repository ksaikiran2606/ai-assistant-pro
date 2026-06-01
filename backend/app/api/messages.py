"""Message and AI streaming API routes."""

import json

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.config import get_settings
from app.core.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas import MessageCreate, MessageListResponse, MessageResponse
from app.services import chat_service
from app.services.ai_service import AIProviderError, ai_service, friendly_ai_error

settings = get_settings()

router = APIRouter(tags=["Messages"])


@router.get("/messages/{chat_id}", response_model=MessageListResponse)
def get_messages(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    chat = chat_service.get_chat(db, chat_id, current_user.id)
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    messages = chat_service.get_chat_messages(db, chat_id)
    return MessageListResponse(
        messages=[MessageResponse.model_validate(m) for m in messages],
        total=len(messages),
    )


@router.post("/messages")
async def send_message(
    data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    chat = chat_service.get_chat(db, data.chat_id, current_user.id)
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    # Save user message
    chat_service.create_message(db, data.chat_id, "user", data.content)

    # Auto-title from first message
    msg_count = chat_service.get_message_count_for_chat(db, data.chat_id)
    if msg_count == 1 and chat.title == "New Chat":
        title = data.content[:50] + ("..." if len(data.content) > 50 else "")
        chat_service.update_chat_title(db, chat, title)

    ai_messages = chat_service.build_ai_messages(db, data.chat_id)

    async def event_stream():
        full_response = ""
        try:
            async for chunk in ai_service.stream_response(ai_messages):
                full_response += chunk
                yield f"data: {json.dumps({'content': chunk})}\n\n"
        except AIProviderError as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            return
        except Exception as e:
            yield f"data: {json.dumps({'error': friendly_ai_error(e, settings.ai_provider)})}\n\n"
            return

        # Persist assistant response
        if full_response:
            chat_service.create_message(db, data.chat_id, "assistant", full_response)

        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
