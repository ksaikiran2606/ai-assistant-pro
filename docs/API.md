# AI Assistant Pro — API Documentation

Base URL: `http://localhost:8000/api` (development)

Interactive docs: `http://localhost:8000/docs`

## Authentication

All protected endpoints require a Bearer token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

---

### POST `/auth/register`

Register a new user account.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response (201):**
```json
{
  "access_token": "eyJhbG...",
  "token_type": "bearer"
}
```

---

### POST `/auth/login`

Authenticate an existing user.

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbG...",
  "token_type": "bearer"
}
```

---

### POST `/auth/logout`

Invalidate session (client-side token discard). Requires auth.

**Response (200):**
```json
{
  "message": "Logged out successfully"
}
```

---

### GET `/auth/me`

Get current authenticated user. Requires auth.

**Response (200):**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "created_at": "2026-01-01T00:00:00Z"
}
```

---

## Chats

### GET `/chats`

List all chats for the authenticated user.

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| search | string | Filter chats by title (optional) |

**Response (200):**
```json
{
  "chats": [
    {
      "id": 1,
      "user_id": 1,
      "title": "Python REST API",
      "created_at": "2026-01-01T00:00:00Z",
      "message_count": 4
    }
  ],
  "total": 1
}
```

---

### POST `/chats`

Create a new chat conversation.

**Request Body:**
```json
{
  "title": "New Chat"
}
```

**Response (201):** Chat object

---

### PATCH `/chats/{id}`

Rename a chat conversation.

**Request Body:**
```json
{
  "title": "Updated Title"
}
```

**Response (200):** Updated chat object

---

### DELETE `/chats/{id}`

Delete a chat and all its messages.

**Response (204):** No content

---

## Messages

### GET `/messages/{chat_id}`

Get all messages for a chat.

**Response (200):**
```json
{
  "messages": [
    {
      "id": 1,
      "chat_id": 1,
      "role": "user",
      "content": "Hello!",
      "created_at": "2026-01-01T00:00:00Z"
    },
    {
      "id": 2,
      "chat_id": 1,
      "role": "assistant",
      "content": "Hello! How can I help you?",
      "created_at": "2026-01-01T00:00:01Z"
    }
  ],
  "total": 2
}
```

---

### POST `/messages`

Send a message and receive a streaming AI response (Server-Sent Events).

**Request Body:**
```json
{
  "chat_id": 1,
  "content": "Explain async/await in Python"
}
```

**Response:** `text/event-stream`

```
data: {"content": "Async"}
data: {"content": "/await"}
data: {"done": true}
```

Error event:
```
data: {"error": "OpenAI API key not configured"}
```

---

## Profile

### GET `/profile`

Get user dashboard data. Requires auth.

**Response (200):**
```json
{
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "created_at": "2026-01-01T00:00:00Z"
  },
  "total_chats": 5,
  "total_messages": 42,
  "recent_chats": [...]
}
```

---

## Health Check

### GET `/health`

**Response (200):**
```json
{
  "status": "healthy",
  "app": "AI Assistant Pro"
}
```

---

## Error Responses

| Status | Description |
|--------|-------------|
| 400 | Validation error |
| 401 | Unauthorized / invalid token |
| 404 | Resource not found |
| 429 | Rate limit exceeded |
| 500 | Internal server error |

```json
{
  "detail": "Error message"
}
```
