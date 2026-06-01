# AI Assistant Pro

A production-ready AI Chatbot SaaS application built with **React**, **FastAPI**, **MySQL**, and **OpenAI/Gemini** integration. Designed as a portfolio-grade full-stack project for Python developers.

![Tech Stack](https://img.shields.io/badge/React-18-61DAFB?style=flat&logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi)
![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=flat&logo=mysql&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-06B6D4?style=flat&logo=tailwindcss)

## Features

- **Authentication** — Register, login, logout with JWT tokens and protected routes
- **Multi-conversation Chat** — Create, rename, delete, and search conversations
- **AI Streaming** — Real-time SSE streaming responses with OpenAI or Gemini
- **Rich Markdown** — Code syntax highlighting, copy buttons, GFM support
- **Dashboard** — User stats, account info, recent conversations
- **Export** — Download chats as PDF or TXT
- **Modern UI** — ChatGPT-inspired design, dark/light theme, fully responsive
- **Security** — Bcrypt password hashing, CORS, rate limiting, input validation

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| Frontend | React 18, Vite, Tailwind CSS, React Router, Axios, React Markdown |
| Backend | FastAPI, SQLAlchemy, Alembic, Pydantic, JWT, SlowAPI |
| Database | MySQL 8.0 |
| AI | OpenAI API / Google Gemini API |
| Deployment | Vercel (frontend), Render (backend) + MySQL host |

## Project Structure

```
Simple_ChatBoot/
├── backend/
│   ├── app/
│   │   ├── api/           # Route handlers (auth, chats, messages, profile)
│   │   ├── core/          # Security, dependencies
│   │   ├── models/        # SQLAlchemy ORM models
│   │   ├── schemas/       # Pydantic validation schemas
│   │   ├── services/      # Business logic & AI service
│   │   ├── config.py      # Environment configuration
│   │   ├── database.py    # DB engine & session
│   │   └── main.py        # FastAPI app entry point
│   ├── alembic/           # Database migrations
│   ├── requirements.txt
│   └── render.yaml        # Render deployment blueprint
├── frontend/
│   ├── src/
│   │   ├── api/           # Axios API client
│   │   ├── components/    # Reusable UI components
│   │   ├── context/       # Auth & theme providers
│   │   ├── hooks/         # Custom React hooks
│   │   ├── pages/         # Route pages
│   │   └── utils/         # Export utilities
│   └── vercel.json
└── docs/
    ├── API.md
    ├── DATABASE.md
    └── DEPLOYMENT.md
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- MySQL 8.0+ (or MariaDB 10.5+)

### 1. Database Setup

```sql
CREATE DATABASE ai_assistant_pro CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env with your DATABASE_URL, SECRET_KEY, and OPENAI_API_KEY

alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### 3. Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

App: http://localhost:5173

## Environment Variables

### Backend (`backend/.env`)

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | MySQL connection string (`mysql+pymysql://user:pass@host:3306/db`) |
| `SECRET_KEY` | JWT signing secret |
| `AI_PROVIDER` | `groq`, `openai`, or `gemini` |
| `GROQ_API_KEY` | Groq API key (free tier — recommended for testing) |
| `GROQ_MODEL` | e.g. `llama-3.3-70b-versatile` |
| `OPENAI_API_KEY` | OpenAI API key |
| `GEMINI_API_KEY` | Gemini API key (if using Gemini) |
| `CORS_ORIGINS` | Allowed frontend origins |

### Frontend (`frontend/.env`)

| Variable | Description |
|----------|-------------|
| `VITE_API_URL` | Backend API URL (e.g. `http://localhost:8000`) |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register user |
| POST | `/api/auth/login` | Login |
| POST | `/api/auth/logout` | Logout |
| GET | `/api/chats` | List chats |
| POST | `/api/chats` | Create chat |
| PATCH | `/api/chats/{id}` | Rename chat |
| DELETE | `/api/chats/{id}` | Delete chat |
| GET | `/api/messages/{chat_id}` | Get messages |
| POST | `/api/messages` | Send message (SSE stream) |
| GET | `/api/profile` | User dashboard |

Full API documentation: [docs/API.md](docs/API.md)

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+K` / `Cmd+K` | New chat |
| `Ctrl+/` / `Cmd+/` | Focus message input |
| `Enter` | Send message |
| `Shift+Enter` | New line |
| `Escape` | Close mobile sidebar |

## Deployment

See the complete guide: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

- **Frontend** → Vercel (set `VITE_API_URL`)
- **Backend** → Render Web Service
- **Database** → MySQL (local, PlanetScale, Railway, Aiven, etc.)

## Database Schema

See: [docs/DATABASE.md](docs/DATABASE.md)

## License

MIT License — free to use for personal and portfolio projects.

## Author

Built as a portfolio project demonstrating full-stack Python development with modern web technologies.
