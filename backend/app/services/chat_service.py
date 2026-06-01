"""Chat and message business logic."""

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.chat import Chat
from app.models.message import Message
from app.models.user import User


def get_user_chats(db: Session, user_id: int, search: str | None = None) -> list[Chat]:
    query = db.query(Chat).filter(Chat.user_id == user_id)
    if search:
        query = query.filter(Chat.title.ilike(f"%{search}%"))
    return query.order_by(Chat.created_at.desc()).all()


def create_chat(db: Session, user_id: int, title: str = "New Chat") -> Chat:
    chat = Chat(user_id=user_id, title=title)
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat


def get_chat(db: Session, chat_id: int, user_id: int) -> Chat | None:
    return (
        db.query(Chat)
        .filter(Chat.id == chat_id, Chat.user_id == user_id)
        .first()
    )


def update_chat_title(db: Session, chat: Chat, title: str) -> Chat:
    chat.title = title
    db.commit()
    db.refresh(chat)
    return chat


def delete_chat(db: Session, chat: Chat) -> None:
    db.delete(chat)
    db.commit()


def get_chat_messages(db: Session, chat_id: int) -> list[Message]:
    return (
        db.query(Message)
        .filter(Message.chat_id == chat_id)
        .order_by(Message.created_at.asc())
        .all()
    )


def create_message(db: Session, chat_id: int, role: str, content: str) -> Message:
    message = Message(chat_id=chat_id, role=role, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def get_message_count_for_chat(db: Session, chat_id: int) -> int:
    return db.query(func.count(Message.id)).filter(Message.chat_id == chat_id).scalar() or 0


def get_user_stats(db: Session, user: User) -> dict:
    total_chats = db.query(func.count(Chat.id)).filter(Chat.user_id == user.id).scalar() or 0
    total_messages = (
        db.query(func.count(Message.id))
        .join(Chat)
        .filter(Chat.user_id == user.id)
        .scalar()
        or 0
    )
    recent_chats = (
        db.query(Chat)
        .filter(Chat.user_id == user.id)
        .order_by(Chat.created_at.desc())
        .limit(5)
        .all()
    )
    return {
        "total_chats": total_chats,
        "total_messages": total_messages,
        "recent_chats": recent_chats,
    }


def build_ai_messages(db: Session, chat_id: int) -> list[dict[str, str]]:
    """Build conversation history for AI context (includes saved user message)."""
    history = get_chat_messages(db, chat_id)
    messages = [
        {
            "role": "system",
            "content": (
                "You are AI Assistant Pro, a helpful, accurate, and friendly AI assistant. "
                "Format responses using Markdown when appropriate. Use code blocks for code."
            ),
        }
    ]
    for msg in history:
        messages.append({"role": msg.role, "content": msg.content})
    return messages
