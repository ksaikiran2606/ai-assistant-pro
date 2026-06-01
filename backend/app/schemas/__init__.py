"""Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ── Auth ──────────────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    created_at: datetime


# ── Chat ──────────────────────────────────────────────────────────────────────

class ChatCreate(BaseModel):
    title: Optional[str] = Field(default="New Chat", max_length=255)


class ChatUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)


class ChatResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    created_at: datetime
    message_count: Optional[int] = 0


class ChatListResponse(BaseModel):
    chats: List[ChatResponse]
    total: int


# ── Message ───────────────────────────────────────────────────────────────────

class MessageCreate(BaseModel):
    chat_id: int
    content: str = Field(..., min_length=1, max_length=32000)


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    chat_id: int
    role: str
    content: str
    created_at: datetime


class MessageListResponse(BaseModel):
    messages: List[MessageResponse]
    total: int


# ── Profile / Dashboard ───────────────────────────────────────────────────────

class ProfileResponse(BaseModel):
    user: UserResponse
    total_chats: int
    total_messages: int
    recent_chats: List[ChatResponse]
