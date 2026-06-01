# Deployment Walkthrough — Beginner Friendly

Deploy in this order: **GitHub → Database → Render (backend) → Vercel (frontend)**

---

## Phase 0 — Push code to GitHub (required first)

Both Render and Vercel deploy from GitHub.

### Step 0.1 — Create GitHub account
Go to https://github.com and sign up (if you don't have one).

### Step 0.2 — Create a new repository
1. Click **+** → **New repository**
2. Name: `ai-assistant-pro`
3. Set to **Private** (recommended — keeps API keys out of public view)
4. Do **NOT** add README, .gitignore, or license (project already has them)
5. Click **Create repository**

### Step 0.3 — Initialize git in your project folder

Open PowerShell in your project folder:

```powershell
cd C:\Users\DELL\OneDrive\Desktop\Simple_ChatBoot
git init
git add .
git commit -m "Initial commit: AI Assistant Pro full stack app"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ai-assistant-pro.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

> **Important:** `.env` is in `.gitignore` — your secrets will NOT be uploaded. Good!

---

## Phase 1 — Cloud MySQL database

Render does not offer free MySQL. Use **Railway** (easiest for beginners).

### Step 1.1 — Create Railway account
1. Go to https://railway.app
2. Sign up with GitHub

### Step 1.2 — Create MySQL database
1. Click **New Project**
2. Click **Provision MySQL**
3. Wait until MySQL is running
4. Click the **MySQL** service → **Variables** tab
5. Copy these values:
   - `MYSQLHOST`
   - `MYSQLPORT`
   - `MYSQLUSER`
   - `MYSQLPASSWORD`
   - `MYSQLDATABASE`

### Step 1.3 — Build your DATABASE_URL

Format:
```
mysql+pymysql://USER:PASSWORD@HOST:PORT/DATABASE
```

**If password has special characters**, URL-encode them:
- `@` → `%40`
- `#` → `%23`

**Example:**
```
mysql+pymysql://root:abc123@containers-us-west-123.railway.app:6543/railway
```

Save this string — you'll paste it into Render in Phase 2.

### Step 1.4 — Allow remote connections
Railway MySQL allows remote connections by default. No extra setup needed.

---

## Phase 2 — Deploy backend on Render

### Step 2.1 — Create Render account
1. Go to https://render.com
2. Sign up with GitHub

### Step 2.2 — Create Web Service
1. Click **New +** → **Web Service**
2. Connect your GitHub repo `ai-assistant-pro`
3. Configure:

| Setting | Value |
|---------|-------|
| **Name** | `ai-assistant-pro-api` |
| **Root Directory** | `backend` |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | Free |

4. Click **Advanced** → add Environment Variables:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | Your Railway MySQL URL from Phase 1 |
| `SECRET_KEY` | Long random string (e.g. run `openssl rand -hex 32` or use a password generator) |
| `AI_PROVIDER` | `groq` |
| `GROQ_API_KEY` | Your Groq key from console.groq.com |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` |
| `CORS_ORIGINS` | `http://localhost:5173` *(update after Vercel deploy)* |

5. Click **Create Web Service**
6. Wait 5–10 minutes for first deploy

### Step 2.3 — Verify backend works
When deploy finishes, open:

```
https://ai-assistant-pro-api.onrender.com/health
```

You should see:
```json
{"status":"healthy","app":"AI Assistant Pro"}
```

Also check API docs:
```
https://ai-assistant-pro-api.onrender.com/docs
```

**Copy your Render URL** — you'll need it for Vercel:
```
https://ai-assistant-pro-api.onrender.com
```

### Step 2.4 — If deploy fails
Click **Logs** tab on Render. Common fixes:

| Error | Fix |
|-------|-----|
| Database connection failed | Check `DATABASE_URL` format and password encoding |
| Module not found | Ensure Root Directory is `backend` |
| Alembic error | Check MySQL is running on Railway |

---

## Phase 3 — Deploy frontend on Vercel

### Step 3.1 — Create Vercel account
1. Go to https://vercel.com
2. Sign up with GitHub

### Step 3.2 — Import project
1. Click **Add New…** → **Project**
2. Import your `ai-assistant-pro` repo
3. Configure:

| Setting | Value |
|---------|-------|
| **Framework Preset** | Vite |
| **Root Directory** | `frontend` |
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |

4. Expand **Environment Variables** and add:

| Key | Value |
|-----|-------|
| `VITE_API_URL` | `https://ai-assistant-pro-api.onrender.com` |

*(Use YOUR actual Render URL — no trailing slash)*

5. Click **Deploy**
6. Wait 2–3 minutes

### Step 3.3 — Get your live URL
After deploy, Vercel gives you a URL like:
```
https://ai-assistant-pro.vercel.app
```

Open it in browser — you should see the login page!

---

## Phase 4 — Connect frontend + backend (CORS)

Your frontend is on Vercel, backend on Render. They must trust each other.

### Step 4.1 — Update CORS on Render
1. Go to Render → your web service → **Environment**
2. Edit `CORS_ORIGINS`:
   ```
   https://ai-assistant-pro.vercel.app,http://localhost:5173
   ```
   *(Use YOUR actual Vercel URL)*
3. Save — Render will redeploy automatically

### Step 4.2 — Test the full app
1. Open your Vercel URL
2. **Register** a new account
3. **Login**
4. Send a chat message
5. Check **Dashboard**

---

## Phase 5 — Final checklist

```
[ ] GitHub repo created and code pushed
[ ] Railway MySQL running
[ ] Render backend: /health returns healthy
[ ] Vercel frontend loads login page
[ ] CORS_ORIGINS includes Vercel URL
[ ] Register + login works
[ ] AI chat responds
[ ] Dashboard shows stats
```

---

## Important notes for free tier

| Platform | Limitation |
|----------|------------|
| **Render** | Backend sleeps after 15 min idle — first request takes ~30 sec to wake |
| **Railway** | $5 free credit/month — enough for testing |
| **Vercel** | Generous free tier for personal projects |
| **Groq** | Free tier with rate limits |

---

## Quick reference — your URLs

Fill in after deploy:

| Service | URL |
|---------|-----|
| Frontend (Vercel) | `https://____________.vercel.app` |
| Backend (Render) | `https://____________.onrender.com` |
| Database (Railway) | *(connection string in Render env only)* |

---

## Need help on a specific step?

Tell me which phase you're on:
- **Phase 0** — GitHub push
- **Phase 1** — Railway MySQL
- **Phase 2** — Render backend
- **Phase 3** — Vercel frontend
- **Phase 4** — CORS / connection issues

We'll do them one at a time together.
