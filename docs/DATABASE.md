# Database Schema — AI Assistant Pro

**Engine:** MySQL 8.0+ (InnoDB, `utf8mb4` charset)

## Entity Relationship Diagram

```
┌─────────────┐       ┌─────────────┐       ┌──────────────┐
│    users    │       │    chats    │       │   messages   │
├─────────────┤       ├─────────────┤       ├──────────────┤
│ id (PK)     │──┐    │ id (PK)     │──┐    │ id (PK)      │
│ name        │  └───>│ user_id(FK) │  └───>│ chat_id (FK) │
│ email       │       │ title       │       │ role         │
│ password    │       │ created_at  │       │ content      │
│ created_at  │       └─────────────┘       │ created_at   │
└─────────────┘                              └──────────────┘
```

## Tables

### users

| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO INCREMENT |
| name | VARCHAR(100) | NOT NULL |
| email | VARCHAR(255) | NOT NULL, UNIQUE, INDEX |
| password | VARCHAR(255) | NOT NULL (bcrypt hash) |
| created_at | DATETIME | NOT NULL |

### chats

| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO INCREMENT |
| user_id | INTEGER | NOT NULL, FK → users.id ON DELETE CASCADE |
| title | VARCHAR(255) | NOT NULL, DEFAULT 'New Chat' |
| created_at | DATETIME | NOT NULL |

**Indexes:** `user_id`

### messages

| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO INCREMENT |
| chat_id | INTEGER | NOT NULL, FK → chats.id ON DELETE CASCADE |
| role | VARCHAR(20) | NOT NULL (`user`, `assistant`, `system`) |
| content | TEXT | NOT NULL |
| created_at | DATETIME | NOT NULL |

**Indexes:** `chat_id`

## Relationships

- **User → Chats:** One-to-many. Deleting a user cascades to all their chats.
- **Chat → Messages:** One-to-many. Deleting a chat cascades to all its messages.

## Migrations

Managed with Alembic. Initial migration: `001_initial_schema.py`

```bash
# Apply migrations
alembic upgrade head

# Create new migration after model changes
alembic revision --autogenerate -m "description"

# Rollback one step
alembic downgrade -1
```

## Sample Queries

```sql
-- User stats
SELECT u.name, COUNT(DISTINCT c.id) AS chats, COUNT(m.id) AS messages
FROM users u
LEFT JOIN chats c ON c.user_id = u.id
LEFT JOIN messages m ON m.chat_id = c.id
WHERE u.id = 1
GROUP BY u.id;

-- Recent conversations
SELECT c.*, COUNT(m.id) AS message_count
FROM chats c
LEFT JOIN messages m ON m.chat_id = c.id
WHERE c.user_id = 1
GROUP BY c.id
ORDER BY c.created_at DESC
LIMIT 10;
```
