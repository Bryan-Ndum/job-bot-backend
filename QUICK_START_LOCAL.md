# Quick Start - Using the Website Locally

## 🚀 3-Step Quick Start

### Step 1: Start the Server

```bash
uvicorn app.main:app --reload --port 8000
```

### Step 2: Open Browser

Go to:
```
http://localhost:8000/dashboard
```

### Step 3: Start Using!

Fill out the form and click "Start Job Discovery" 🎉

---

## 📋 What You'll See

1. **Dashboard Page** with:
   - Stats cards (Jobs Discovered, Applications Submitted, etc.)
   - Configuration form
   - Start button

2. **Fill out the form**:
   - Search keywords (e.g., "cybersecurity analyst")
   - Location (e.g., "North Carolina")
   - Select job boards (LinkedIn, Indeed, etc.)
   - Your personal information

3. **Click "Start Job Discovery"**

4. **Watch it work**:
   - Progress updates
   - Jobs being discovered
   - Applications being submitted
   - Results displayed

---

## 🔧 Troubleshooting

### "Can't connect to API"

**Fix**: Make sure FastAPI server is running on port 8000

```bash
uvicorn app.main:app --reload --port 8000
```

### "404 Not Found" on /dashboard

**Fix**: Make sure `frontend` folder exists and has `index.html`

### Port already in use

**Fix**: Use a different port:

```bash
uvicorn app.main:app --reload --port 8001
```

Then go to: `http://localhost:8001/dashboard`

---

## 🌐 Want to Access from Phone/Other Device?

On the same WiFi network:

1. Find your computer's IP address:
   - **Windows**: `ipconfig` → Look for IPv4 Address
   - **Mac/Linux**: `ifconfig` → Look for inet

2. Start server with:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. Access from phone/other device:
   ```
   http://YOUR_IP:8000/dashboard
   ```
   Example: `http://192.168.1.100:8000/dashboard`

---

## 🎯 That's It!

You're now using the website locally. No domain needed! 

When you're ready to go live, see `LOCAL_WEBSITE_GUIDE.md` for domain setup.






