# Quick Fix - If start_local_server.bat Doesn't Work

## ✅ Try This First (Most Common Fix)

Open **Command Prompt** (not PowerShell) and run:

```bash
cd "C:\Users\bryan\OneDrive\Desktop\Job app bot"
python -m uvicorn app.main:app --reload --port 8000
```

This should work! Then open: `http://localhost:8000/dashboard`

---

## 🔍 If That Doesn't Work

### Step 1: Check Your Setup

Double-click: `check_setup.bat`

This will tell you what's missing.

### Step 2: Install Missing Dependencies

Double-click: `INSTALL_DEPENDENCIES.bat`

### Step 3: Try Again

Run the command from Step 1 again.

---

## 🚀 Alternative: Use Python Directly

Instead of the batch file, just run this every time:

```bash
python -m uvicorn app.main:app --reload --port 8000
```

Then open browser to: `http://localhost:8000/dashboard`

---

## 💡 Pro Tip

Create a desktop shortcut:

1. Right-click on your desktop → New → Shortcut
2. Target: `C:\Windows\System32\cmd.exe /k "cd /d C:\Users\bryan\OneDrive\Desktop\Job app bot && python -m uvicorn app.main:app --reload --port 8000"`
3. Name: "Job Bot Server"
4. Double-click to start!

---

## ❓ Still Not Working?

Tell me:
1. What happens when you double-click `start_local_server.bat`? (Does it close? Show an error?)
2. What happens when you run `python -m uvicorn app.main:app --reload --port 8000` in Command Prompt?
3. What error message do you see?






