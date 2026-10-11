# DataPulse Zero-Cost Deployment Guide

Deploy DataPulse to the cloud at **₹0 cost** using free tiers of modern developer platforms.

---

## 1. Cloud Architecture Overview (Free Tier)

| Service | Component | Free Tier Provider | Cost |
| :--- | :--- | :--- | :--- |
| **Frontend** | React (Vite) Single Page App | **Vercel** or **Netlify** | **₹0** (Unlimited bandwidth / month) |
| **Backend API** | FastAPI Web Service | **Render** or **Railway** or **Fly.io** | **₹0** (750 free compute hours / month) |
| **Database** | Managed PostgreSQL Instance | **Neon** or **Supabase** or **Render Postgres** | **₹0** (Free PostgreSQL instance) |

---

## 2. Step-by-Step Free Cloud Deployment

### Step A: Free Managed PostgreSQL Database
1. Create a free account on [Neon.tech](https://neon.tech) or [Supabase.com](https://supabase.com).
2. Create a new PostgreSQL database named `datapulse_db`.
3. Copy your database connection string:
   ```text
   postgresql://[user]:[password]@[host]:5432/datapulse_db?sslmode=require
   ```

### Step B: Deploy FastAPI Backend (Render)
1. Push your repository to your GitHub profile.
2. Log into [Render.com](https://render.com) and click **New Web Service**.
3. Select your `DataPulse` GitHub repository.
4. Set the following build options:
   * **Root Directory**: `.`
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `python -m uvicorn backend.main:app --host 0.0.0.0 --port 10000`
5. Under **Environment Variables**, add:
   * `DATABASE_URL`: Your PostgreSQL connection string from Step A.
6. Click **Deploy**. Your API is live at `https://your-service.onrender.com`.

### Step C: Deploy React Frontend (Vercel)
1. Log into [Vercel.com](https://vercel.com) and click **Add New Project**.
2. Select your `DataPulse` repository.
3. Set:
   * **Root Directory**: `frontend`
   * **Framework Preset**: `Vite`
   * **Build Command**: `npm run build`
   * **Output Directory**: `dist`
4. Click **Deploy**. Your dashboard is now live globally with free SSL!

---

## 3. Local Containerized Deployment (Docker)

If you have Docker Desktop installed, you can launch the complete ecosystem locally with one command:

```powershell
docker compose up --build
```
