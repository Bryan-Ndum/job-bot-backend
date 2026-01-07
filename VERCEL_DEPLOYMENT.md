# Deploying to Vercel - Complete Guide

## 🏗️ Architecture Overview

When deploying to Vercel, you'll have:

```
Frontend (Vercel)          Backend (Railway/Render/Fly.io)
    ↓                              ↓
  Static Files          FastAPI Server (Python)
  HTML/CSS/JS          API Endpoints
  React/Vue/etc.       Database Connections
```

**Frontend → Backend Communication:**
- Frontend makes API calls to your backend
- Backend URL configured via environment variables
- CORS enabled on backend for cross-origin requests

---

## 📦 Part 1: Deploy Frontend to Vercel

### Step 1: Prepare Your Frontend

Your frontend is already ready! The files are in `frontend/` directory.

### Step 2: Install Vercel CLI (Optional)

```bash
npm i -g vercel
```

### Step 3: Deploy via Vercel Dashboard (Recommended)

1. **Go to Vercel**: https://vercel.com
2. **Sign up/Login** (GitHub integration recommended)
3. **Click "Add New Project"**
4. **Import your repository** (or upload files)
5. **Configure project**:
   - **Root Directory**: `frontend` (important!)
   - **Framework Preset**: Other
   - **Build Command**: (leave empty - it's static)
   - **Output Directory**: `.` (current directory)
6. **Environment Variables**:
   - Add: `VITE_API_URL` or `REACT_APP_API_URL` = `https://your-backend-url.railway.app`
   - This will be your FastAPI backend URL (we'll set this up next)

### Step 4: Deploy via CLI (Alternative)

```bash
cd frontend
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? (select your account)
# - Link to existing project? No
# - Project name? job-application-bot
# - Directory? ./
# - Override settings? No
```

### Step 5: Set Environment Variables in Vercel

In Vercel Dashboard → Your Project → Settings → Environment Variables:

```
VITE_API_URL=https://your-backend-url.railway.app
# OR
REACT_APP_API_URL=https://your-backend-url.railway.app
```

Update `frontend/app.js` to use this:
```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 
                     process.env.REACT_APP_API_URL || 
                     (window.location.hostname === 'localhost' ? 'http://localhost:8000' : 'https://your-backend-url.railway.app');
```

---

## 🚀 Part 2: Deploy Backend (FastAPI)

Vercel doesn't support long-running Python servers well. Use one of these:

### Option A: Railway (Recommended - Easiest)

1. **Go to Railway**: https://railway.app
2. **Sign up with GitHub**
3. **New Project** → **Deploy from GitHub repo**
4. **Add Service** → **GitHub Repo** (select your repo)
5. **Configure**:
   - Railway auto-detects Python
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**: Add all your `.env` variables
6. **Get your URL**: Railway provides a URL like `https://your-app.railway.app`

**Railway Configuration File** (`railway.json` - optional):
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**Create `Procfile`** (for Railway):
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Option B: Render (Good Alternative)

1. **Go to Render**: https://render.com
2. **New** → **Web Service**
3. **Connect GitHub** → Select your repo
4. **Configure**:
   - **Name**: job-app-bot-backend
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. **Environment Variables**: Add all `.env` variables
6. **Deploy**

### Option C: Fly.io (Great for Global Distribution)

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Launch app
fly launch

# Set secrets (environment variables)
fly secrets set OPENAI_API_KEY=your-key
fly secrets set SUPABASE_URL=your-url
# ... etc

# Deploy
fly deploy
```

**Create `fly.toml`**:
```toml
app = "your-app-name"
primary_region = "iad"

[build]

[env]
  PORT = "8080"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = false
  auto_start_machines = true
  min_machines_running = 1
  processes = ["app"]

[[services]]
  protocol = "tcp"
  internal_port = 8080
```

---

## 🔗 Part 3: Connect Frontend to Backend

### Update Frontend API URL

After deploying backend, get your backend URL and update:

1. **In Vercel Dashboard**:
   - Go to your project → Settings → Environment Variables
   - Add: `VITE_API_URL` = `https://your-backend-url.railway.app`

2. **Update `frontend/app.js`** to read from environment:
```javascript
const API_BASE_URL = 
  window.location.hostname === 'localhost' 
    ? 'http://localhost:8000'
    : (import.meta.env?.VITE_API_URL || 
       process.env?.REACT_APP_API_URL || 
       'https://your-backend-url.railway.app');
```

3. **Redeploy frontend** so it picks up the new environment variable

### Test Connection

Open your Vercel frontend URL and check browser console. You should see:
- ✅ API is healthy and ready

If you see CORS errors, make sure your backend has CORS enabled (already done in `app/main.py`).

---

## 📝 Part 4: Create Required Files

### Create `requirements.txt` (if not exists)

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-dotenv==1.0.0
openai==1.3.0
supabase==2.0.0
playwright==1.40.0
pydantic==2.5.0
requests==2.31.0
```

### Create `runtime.txt` (for Render/Railway)

```
python-3.11.0
```

### Create `Procfile` (for Railway/Render)

```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

## 🔐 Part 5: Environment Variables Setup

### Backend Environment Variables (Railway/Render/Fly.io)

Add these in your hosting platform's dashboard:

**Required:**
```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxx
```

**Optional:**
```
CAPTCHA_2CAPTCHA_API_KEY=xxxxxxxxxxxxx
PORT=8000
```

### Frontend Environment Variables (Vercel)

```
VITE_API_URL=https://your-backend-url.railway.app
# OR
REACT_APP_API_URL=https://your-backend-url.railway.app
```

---

## 🧪 Part 6: Testing Deployment

### 1. Test Backend

```bash
curl https://your-backend-url.railway.app/api/jobs/health
```

Should return:
```json
{"status": "healthy", "system": "job-application-orchestrator"}
```

### 2. Test Frontend

1. Open your Vercel URL: `https://your-app.vercel.app`
2. Open browser console (F12)
3. Check for any errors
4. Try the health check button

### 3. Test Full Flow

1. Fill in the form
2. Start a small job discovery (1 job board, 5 jobs)
3. Watch it work!

---

## 🎯 Quick Deployment Checklist

### Frontend (Vercel)
- [ ] Push code to GitHub
- [ ] Connect Vercel to GitHub repo
- [ ] Set root directory to `frontend`
- [ ] Add environment variable: `VITE_API_URL` or `REACT_APP_API_URL`
- [ ] Deploy

### Backend (Railway/Render/Fly.io)
- [ ] Push code to GitHub
- [ ] Connect hosting platform to GitHub repo
- [ ] Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] Add all environment variables (OpenAI, Supabase, etc.)
- [ ] Deploy
- [ ] Copy backend URL

### Connect Them
- [ ] Update Vercel env var with backend URL
- [ ] Update `frontend/app.js` to use env var
- [ ] Redeploy frontend
- [ ] Test!

---

## 💡 Pro Tips

### 1. Custom Domain

**Vercel:**
- Settings → Domains → Add domain
- Free SSL certificate included!

**Railway/Render:**
- Settings → Custom Domain
- Point DNS to provided CNAME

### 2. Environment-Specific URLs

Create different backend URLs for:
- Development: `http://localhost:8000`
- Staging: `https://staging-backend.railway.app`
- Production: `https://backend.railway.app`

### 3. Monitoring

- **Vercel**: Built-in analytics
- **Railway**: Built-in logs and metrics
- **Render**: Built-in logs

### 4. Cost Estimates

**Vercel:**
- Free tier: Unlimited for static sites
- Pro: $20/month (if you need more)

**Railway:**
- Free tier: $5 credit/month
- Pro: Pay as you go (~$5-20/month for small apps)

**Render:**
- Free tier: Available (with limitations)
- Starter: $7/month

---

## 🚨 Common Issues

### CORS Errors

**Fix**: Make sure backend has CORS enabled (already done):
```python
app.add_middleware(CORSMiddleware, allow_origins=["*"])
```

### Environment Variables Not Working

**Fix**: 
1. Make sure variable name matches exactly
2. Redeploy after adding variables
3. Check variable value in hosting dashboard

### Backend Not Starting

**Fix**:
- Check logs in hosting platform
- Verify `requirements.txt` has all dependencies
- Make sure start command is correct
- Check PORT environment variable

### Frontend Can't Connect to Backend

**Fix**:
1. Test backend URL directly in browser
2. Check backend is running (check logs)
3. Verify API_BASE_URL in frontend
4. Check CORS settings

---

## 🎉 Success!

Once deployed, you'll have:

✅ **Frontend**: `https://your-app.vercel.app`  
✅ **Backend**: `https://your-backend.railway.app`  
✅ **Full Stack**: Ready to use!

You can now access your job application bot from anywhere in the world! 🌍






