# ⚡ Quick Start Guide - Apply to Jobs in 5 Minutes

## Prerequisites Checklist

- [ ] API keys in `.env` file (OpenAI, Supabase)
- [ ] Database tables created
- [ ] Playwright installed (`python -m playwright install chromium`)

**Quick Check:**
```bash
python Scripts/check_playwright.py
python Scripts/create_missing_tables.py
```

---

## 🚀 Apply to Your First Job (3 Steps)

### Step 1: Create Application Script

Create `apply_job.py`:

```python
import sys
import os
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.services.job_application_orchestrator import apply_to_job

result = apply_to_job(
    url="https://linkedin.com/jobs/view/YOUR_JOB_ID",
    job_description="Paste job description here...",
    user_id="your_user_id",
    user_info={
        "first_name": "Bryan",
        "last_name": "Ndum",
        "email": "bryanndum12@gmail.com"
    },
    auto_apply=True  # Set True to actually apply
)

print(f"Fit Score: {result.get('fit_score')}")
print(f"Status: {result.get('status')}")
```

### Step 2: Fill in Your Details

- Replace `YOUR_JOB_ID` with actual LinkedIn job ID
- Paste the job description
- Update your user info

### Step 3: Run It

```bash
python apply_job.py
```

**That's it!** The system will:
1. ✅ Parse the job
2. ✅ Score it (0-100)
3. ✅ Generate tailored resume
4. ✅ Generate cover letter
5. ✅ Apply automatically (if `auto_apply=True`)

---

## 📊 Understanding Results

- **Fit Score >= 80**: High fit, priority apply
- **Fit Score 65-79**: Good fit, apply
- **Fit Score < 65**: Low fit, automatically skipped

**Status:**
- `applied` = ✅ Successfully submitted
- `ready_to_apply` = 📄 Resume generated (set `auto_apply=True` to submit)
- `skipped` = ⏭️ Low fit score

---

## 🔄 Apply to Multiple Jobs

Create `jobs.json`:
```json
[
    {"url": "https://linkedin.com/jobs/view/111", "description": "Job 1..."},
    {"url": "https://linkedin.com/jobs/view/222", "description": "Job 2..."}
]
```

Then:
```python
from app.services.job_application_orchestrator import apply_to_jobs_batch
import json

with open("jobs.json") as f:
    jobs = json.load(f)

result = apply_to_jobs_batch(
    job_inputs=jobs,
    user_id="your_user_id",
    user_info={"email": "your@email.com"},
    auto_apply=True,
    min_score=65  # Only apply to jobs with score >= 65
)

print(f"Applied: {result['applied']}")
print(f"Skipped: {result['skipped']}")
```

---

## 💡 Pro Tips

1. **Start with `auto_apply=False`** to review generated resumes first
2. **Only apply to jobs with fit_score >= 65** for best results
3. **Track callbacks** to optimize over time
4. **Review skipped jobs** to understand why they were skipped

---

## 🆘 Quick Troubleshooting

**"Playwright not found"**
```bash
pip install playwright
python -m playwright install chromium
```

**"Table does not exist"**
- Run SQL from `create_networking_table.sql` in Supabase SQL Editor

**"API key invalid"**
- Check `.env` file exists and keys are correct

---

**Full Guide:** See `USER_GUIDE.md` for detailed instructions






