# Troubleshooting - Local Server Issues

## Common Problems & Solutions

### Problem: Batch file closes immediately

**Symptom**: Double-clicking `start_local_server.bat` opens and closes instantly

**Solutions**:

1. **Run from Command Prompt instead**:
   - Open Command Prompt (cmd)
   - Navigate to your project: `cd "C:\Users\bryan\OneDrive\Desktop\Job app bot"`
   - Run: `start_local_server.bat`
   - This way you'll see any error messages

2. **Run the command directly**:
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Check if Python is in PATH**:
   ```bash
   python --version
   ```
   If this doesn't work, Python isn't in your PATH.

---

### Problem: "Python is not recognized"

**Solution**: Install Python or add it to PATH

1. Install Python from https://www.python.org/
2. **Important**: Check "Add Python to PATH" during installation
3. Restart your computer
4. Test: `python --version`

---

### Problem: "No module named 'uvicorn'"

**Solution**: Install uvicorn

```bash
pip install uvicorn fastapi
```

Or install all dependencies:
```bash
pip install -r requirements.txt
```

---

### Problem: "No module named 'app'"

**Symptom**: ModuleNotFoundError: No module named 'app'

**Solution**: Make sure you're in the correct directory

```bash
cd "C:\Users\bryan\OneDrive\Desktop\Job app bot"
python -m uvicorn app.main:app --reload --port 8000
```

---

### Problem: Port 8000 already in use

**Symptom**: `ERROR: [Errno 10048] Only one usage of each socket address`

**Solution**: Use a different port

```bash
python -m uvicorn app.main:app --reload --port 8001
```

Then access: `http://localhost:8001/dashboard`

---

### Problem: "Failed to import app.main"

**Check**:
1. Make sure `app/main.py` exists
2. Check for syntax errors in `app/main.py`
3. Try: `python -c "from app.main import app"`

---

### Problem: Dashboard page shows 404

**Check**:
1. Make sure `frontend/index.html` exists
2. Check the URL: Should be `http://localhost:8000/dashboard` (not just `/`)
3. Check browser console for errors (F12)

---

## Step-by-Step Diagnostic

Run these commands one by one:

```bash
# 1. Check Python
python --version

# 2. Check if you're in the right directory
cd "C:\Users\bryan\OneDrive\Desktop\Job app bot"
dir app\main.py

# 3. Check if uvicorn is installed
python -m uvicorn --version

# 4. Test if app can be imported
python -c "from app.main import app; print('OK')"

# 5. Try starting the server
python -m uvicorn app.main:app --reload --port 8000
```

If any step fails, that's where the problem is!

---

## Quick Fix Commands

**If nothing works, try this complete reset**:

```bash
# Navigate to project
cd "C:\Users\bryan\OneDrive\Desktop\Job app bot"

# Install/upgrade dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Start server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Getting Help

If you see an error message, note:
1. **What command did you run?**
2. **What's the exact error message?**
3. **What step failed?** (from the diagnostic above)

This will help identify the issue faster!






