# Using the Website Locally & Adding a Custom Domain

## 🖥️ Part 1: Using the Website Locally

### Option A: Using FastAPI to Serve Everything (Recommended)

This is the easiest way - FastAPI will serve both the backend API and the frontend.

#### Step 1: Start the FastAPI Server

```bash
# From your project root directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

#### Step 2: Open the Dashboard

Open your browser and go to:
```
http://localhost:8000/dashboard
```

**OR** just:
```
http://localhost:8000
```
(Then click the dashboard link if you see it, or manually go to `/dashboard`)

That's it! The website is now running locally.

---

### Option B: Separate Frontend Server (Alternative)

If you want to run the frontend separately for development:

#### Step 1: Start FastAPI Backend

```bash
uvicorn app.main:app --reload --port 8000
```

#### Step 2: Start Frontend Server

Open a **new terminal** and run:

```bash
cd frontend
python -m http.server 8080
```

#### Step 3: Open the Website

```
http://localhost:8080
```

**Note**: Make sure `frontend/app.js` has the API URL set to `http://localhost:8000`

---

## 🌐 Part 2: Adding a Custom Domain

### For Local Development (localhost alternatives)

You can use tools to access your local server with a custom local domain:

#### Option 1: Edit Hosts File (Windows/Mac/Linux)

1. **Windows**: Edit `C:\Windows\System32\drivers\etc\hosts`
2. **Mac/Linux**: Edit `/etc/hosts`

Add this line:
```
127.0.0.1    jobbot.local
```

Then access:
```
http://jobbot.local:8000/dashboard
```

#### Option 2: Use ngrok (Access from Internet)

This lets you access your local server from anywhere:

```bash
# Install ngrok: https://ngrok.com/download
# After installation:
ngrok http 8000
```

You'll get a URL like:
```
https://abc123.ngrok.io
```

Access your site at:
```
https://abc123.ngrok.io/dashboard
```

**Free tier**: Limited URLs, but great for testing!

---

## 🌍 Part 3: Adding a Real Domain (Production)

### Step 1: Deploy to Vercel (Frontend)

1. **Deploy your frontend** to Vercel (see `VERCEL_DEPLOYMENT.md`)
2. Your site will be at: `https://your-project.vercel.app`

### Step 2: Add Custom Domain in Vercel

1. Go to **Vercel Dashboard** → Your Project → **Settings** → **Domains**

2. Click **"Add Domain"**

3. Enter your domain name:
   - `jobbot.com` (if you own it)
   - `app.jobbot.com` (subdomain)
   - `www.jobbot.com` (www subdomain)

4. Vercel will show you DNS configuration:
   ```
   Type: CNAME
   Name: @ (or www, or app)
   Value: cname.vercel-dns.com
   ```

### Step 3: Configure DNS at Your Domain Registrar

Go to where you bought your domain (GoDaddy, Namecheap, Google Domains, etc.):

1. **Find DNS Settings** (usually in "DNS Management" or "Domain Settings")

2. **Add DNS Record**:
   - **Type**: CNAME (or A record if Vercel provides IP)
   - **Name**: `@` (root domain) or `www` (for www.yourdomain.com)
   - **Value**: The CNAME value Vercel provided (e.g., `cname.vercel-dns.com`)
   - **TTL**: 3600 (or default)

3. **Save** the DNS record

### Step 4: Wait for DNS Propagation

- DNS changes take **5 minutes to 48 hours** (usually 5-30 minutes)
- Check if it's working: `nslookup yourdomain.com`
- Vercel dashboard will show "Valid Configuration" when ready

### Step 5: SSL Certificate (Automatic!)

- Vercel automatically provides **free SSL certificates**
- Your site will be accessible at `https://yourdomain.com`
- No additional setup needed!

---

## 📝 Example: Complete Domain Setup

### Scenario: You own `jobbot.com`

#### Option A: Use Root Domain (jobbot.com)

1. **In Vercel**: Add domain `jobbot.com`
2. **In DNS** (at your registrar):
   ```
   Type: A
   Name: @
   Value: 76.76.21.21 (Vercel's IP - check Vercel dashboard for current)
   ```
   OR
   ```
   Type: CNAME
   Name: @
   Value: cname.vercel-dns.com
   ```

#### Option B: Use Subdomain (app.jobbot.com)

1. **In Vercel**: Add domain `app.jobbot.com`
2. **In DNS**:
   ```
   Type: CNAME
   Name: app
   Value: cname.vercel-dns.com
   ```

#### Option C: Use www (www.jobbot.com)

1. **In Vercel**: Add domain `www.jobbot.com`
2. **In DNS**:
   ```
   Type: CNAME
   Name: www
   Value: cname.vercel-dns.com
   ```

---

## 🔧 Backend Domain Setup (Railway/Render)

If you also want a custom domain for your backend API:

### Railway

1. **In Railway Dashboard**: Your Project → Settings → Domains
2. **Add Custom Domain**: Enter `api.jobbot.com`
3. **Configure DNS** at your registrar:
   ```
   Type: CNAME
   Name: api
   Value: (Railway provides this)
   ```

### Render

1. **In Render Dashboard**: Your Service → Settings → Custom Domain
2. **Add Domain**: `api.jobbot.com`
3. **Configure DNS**: Render will provide the CNAME value

### Then Update Frontend

Update your frontend's API URL to use the custom domain:

**In Vercel Environment Variables**:
```
VITE_API_URL=https://api.jobbot.com
```

---

## 🚀 Complete Production Setup Example

### Architecture:

```
Frontend: https://jobbot.com (Vercel)
Backend:  https://api.jobbot.com (Railway)
```

### DNS Records (at your domain registrar):

```
Type    Name    Value                   
─────────────────────────────────────
A       @       76.76.21.21            (Vercel frontend)
CNAME   www     cname.vercel-dns.com   (Vercel www)
CNAME   api     railway-provided-url   (Railway backend)
```

### Environment Variables:

**Vercel (Frontend)**:
```
VITE_API_URL=https://api.jobbot.com
```

**Railway (Backend)**:
```
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://...
SUPABASE_SERVICE_KEY=...
```

---

## 🎯 Quick Start Checklist

### Local Usage:
- [ ] Start FastAPI: `uvicorn app.main:app --reload --port 8000`
- [ ] Open browser: `http://localhost:8000/dashboard`
- [ ] Start using the website!

### Custom Domain (Production):
- [ ] Deploy frontend to Vercel
- [ ] Deploy backend to Railway/Render
- [ ] Buy domain (if you don't have one)
- [ ] Add domain in Vercel dashboard
- [ ] Configure DNS at registrar
- [ ] Wait for DNS propagation (5-30 min)
- [ ] Update API URL in frontend env vars
- [ ] ✅ Your site is live at your custom domain!

---

## 💡 Pro Tips

### 1. Domain Providers
Good options:
- **Namecheap**: Cheap, easy to use
- **Google Domains**: Simple interface
- **Cloudflare**: Free privacy, good DNS
- **GoDaddy**: Popular but can be expensive

### 2. Free Domain Options
- **Freenom** (.tk, .ml, .ga domains) - Free but less reliable
- **GitHub Student Pack** - Free .me domain for students

### 3. Testing Locally with Custom Domain
Use `hosts` file to test custom domain locally:
```
127.0.0.1    jobbot.local
127.0.0.1    api.jobbot.local
```

### 4. Multiple Environments
You can have:
- `dev.jobbot.com` → Development
- `staging.jobbot.com` → Staging  
- `jobbot.com` → Production

---

## ❓ Common Questions

**Q: Do I need a domain to use the website?**
A: No! You can use it locally or use Vercel's free subdomain (`your-project.vercel.app`)

**Q: How much does a domain cost?**
A: Usually $10-15/year for .com domains

**Q: Can I use the same domain for frontend and backend?**
A: Yes! Use subdomains:
- `jobbot.com` → Frontend
- `api.jobbot.com` → Backend

**Q: How long does DNS setup take?**
A: Usually 5-30 minutes, but can take up to 48 hours

**Q: Is SSL included?**
A: Yes! Vercel provides free SSL certificates automatically

---

## 🎉 You're Ready!

Once set up, you'll have:
- ✅ Professional domain name
- ✅ Free SSL certificate
- ✅ Fast global CDN
- ✅ Easy to share with others

Enjoy your professional job application bot website! 🚀






