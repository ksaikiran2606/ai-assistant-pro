# Deployment Guide — AI Assistant Pro

## Architecture Overview

| Component | Platform | URL Pattern |
|-----------|----------|-------------|
| Frontend | Vercel | `https://your-app.vercel.app` |
| Backend API | Render | `https://your-api.onrender.com` |
| Database | MySQL (external host) | Connection string via `DATABASE_URL` |

---

## 1. MySQL Database

The app uses **MySQL 8.0+** with the `pymysql` driver. Choose any MySQL provider:

| Provider | Notes |
|----------|-------|
| **Local MySQL** | Best for development |
| **[PlanetScale](https://planetscale.com)** | Serverless MySQL, free tier |
| **[Railway](https://railway.app)** | MySQL add-on, easy setup |
| **[Aiven](https://aiven.io)** | Managed MySQL |
| **AWS RDS / Azure / GCP** | Production-grade |

### Create the database

```sql
CREATE DATABASE ai_assistant_pro CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Connection string format

```
mysql+pymysql://USERNAME:PASSWORD@HOST:3306/ai_assistant_pro
```

**PlanetScale example** (may require SSL — add `?ssl=true` to the URL if needed):

```
mysql+pymysql://user:pass@aws.connect.psdb.cloud/ai_assistant_pro?ssl_ca=/etc/ssl/certs/ca-certificates.crt
```

For local development:

```
mysql+pymysql://root:password@localhost:3306/ai_assistant_pro
```

---

## 2. Backend API (Render)

### Option A: Blueprint Deploy

1. Push code to GitHub
2. In Render: **New +** → **Blueprint**
3. Connect repo and select `backend/render.yaml`
4. Set environment variables:
   - `DATABASE_URL` — your MySQL connection string
   - `OPENAI_API_KEY` — your OpenAI key
   - `CORS_ORIGINS` — your Vercel frontend URL
   - `AI_PROVIDER` — `openai` or `gemini`
   - `GEMINI_API_KEY` — if using Gemini

### Option B: Manual Web Service

1. **New +** → **Web Service**
2. Connect GitHub repo, set root directory to `backend`
3. Configure:
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables from `.env.example` (including `DATABASE_URL`)

### Required Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | MySQL connection string (`mysql+pymysql://...`) |
| `SECRET_KEY` | Random 64-char secret for JWT |
| `CORS_ORIGINS` | Frontend URL(s), comma-separated |
| `OPENAI_API_KEY` | OpenAI API key |
| `AI_PROVIDER` | `openai` or `gemini` |
| `GEMINI_API_KEY` | Gemini key (if using Gemini) |

---

## 3. Frontend (Vercel)

1. Push code to GitHub
2. Log in to [Vercel](https://vercel.com)
3. **Add New Project** → Import repo
4. Set root directory to `frontend`
5. Framework preset: **Vite**
6. Add environment variable:
   ```
   VITE_API_URL=https://your-api.onrender.com
   ```
7. Deploy

The included `vercel.json` handles SPA routing.

---

## 4. Post-Deployment Checklist

- [ ] Backend health check: `GET https://your-api.onrender.com/health`
- [ ] API docs accessible: `https://your-api.onrender.com/docs`
- [ ] CORS origins include your Vercel URL
- [ ] Database migrations ran successfully (check Render logs)
- [ ] Register a test user on production frontend
- [ ] Send a test message and verify AI streaming works
- [ ] Verify JWT auth flow (login/logout)

---

## 5. Custom Domain (Optional)

### Vercel
Settings → Domains → Add your domain

### Render
Settings → Custom Domains → Add domain and configure DNS

Update `CORS_ORIGINS` and `VITE_API_URL` accordingly.

---

## 6. Local Development

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # Edit with your MySQL DATABASE_URL
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
cp .env.example .env
npm run dev
```

Visit `http://localhost:5173`

---

## 7. Troubleshooting

| Issue | Solution |
|-------|----------|
| CORS errors | Add frontend URL to `CORS_ORIGINS` on backend |
| 401 on API calls | Check token in localStorage; verify `SECRET_KEY` is consistent |
| AI not responding | Verify API key; check Render logs for errors |
| DB connection failed | Verify `DATABASE_URL` format; ensure MySQL host allows remote connections |
| Charset/emoji issues | Use `utf8mb4` charset when creating the database |
| Cold start delay | Render free tier sleeps after inactivity (~30s wake time) |
