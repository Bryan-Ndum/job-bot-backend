# 🚀 Complete User Guide - Job Application System

## Step-by-Step Guide to Start Applying to Jobs

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Applying to a Single Job](#applying-to-a-single-job)
4. [Applying to Multiple Jobs (Batch)](#applying-to-multiple-jobs-batch)
5. [Using the API](#using-the-api)
6. [Tracking Applications](#tracking-applications)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you start, make sure you have:

- ✅ Python 3.8+ installed
- ✅ All API keys configured (see `SETUP_REQUIRED_KEYS.md`)
- ✅ Database tables created (see `QUICK_DATABASE_SETUP.md`)
- ✅ Playwright and Chromium installed

**Quick Check:**
```bash
# Verify everything is ready
python Scripts/check_playwright.py
python Scripts/create_missing_tables.py
```

---

## Initial Setup

### Step 1: Verify Your Environment

Check that your `.env` file contains all required keys:

```bash
# Required keys
OPENAI_API_KEY=sk-proj-...
SUPABASE_URL=https://...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Step 2: Test Resume Generation

Test that the system can generate resumes:

```bash
python Tests/test_resume_pipeline.py
```

You should see:
- ✅ Resume generated (HTML and PDF)
- ✅ Cover letter generated

---

## Applying to a Single Job

### Method 1: Using Python Script (Recommended)

Create a file `apply_to_job.py`:

```python
import sys
import os

# Add project root to path
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.services.job_application_orchestrator import apply_to_job

# Your information
user_id = "your_user_id"  # e.g., "bryan_123"
user_info = {
    "first_name": "Bryan",
    "last_name": "Ndum",
    "email": "bryanndum12@gmail.com",
    "phone": "",  # Optional
    "location": "Remote, NC",  # Optional
    "linkedin": ""  # Optional
}

# Job details
job_url = "https://www.linkedin.com/jobs/view/1234567890"
job_description = """
IT Support Analyst

We are looking for an IT Support Analyst to join our team.
Requirements:
- Windows troubleshooting
- Azure cloud services
- Network fundamentals
- IT support experience
"""

# Apply to job
print("🚀 Starting job application process...\n")

result = apply_to_job(
    url=job_url,
    job_description=job_description,
    user_id=user_id,
    user_info=user_info,
    auto_apply=True  # Set to True to actually apply, False to just generate resume
)

# Print results
print("\n" + "="*60)
print("RESULTS")
print("="*60)
print(f"Job ID: {result.get('job_id')}")
print(f"Company: {result.get('company')}")
print(f"Role: {result.get('role')}")
print(f"Fit Score: {result.get('fit_score')}")
print(f"Decision: {result.get('decision')}")
print(f"Status: {result.get('status')}")

if result.get('status') == 'applied':
    print("\n✅ Application submitted successfully!")
    print(f"Application ID: {result.get('application_id')}")
elif result.get('status') == 'ready_to_apply':
    print("\n📄 Resume and cover letter generated")
    print(f"Resume: {result.get('resume_path')}")
    print(f"Cover Letter: {result.get('cover_letter_path')}")
    print("\n⚠️ Set auto_apply=True to actually submit")
elif result.get('status') == 'skipped':
    print(f"\n⏭️ Job skipped: {result.get('reason')}")
else:
    print(f"\n❌ Error: {result.get('error')}")
```

**Run it:**
```bash
python apply_to_job.py
```

### Method 2: Using the Test Script

Edit `Tests/test_job_application_system.py` with your job details, then:

```bash
python Tests/test_job_application_system.py
```

### Method 3: Interactive Python

```python
from app.services.job_application_orchestrator import apply_to_job

result = apply_to_job(
    url="https://linkedin.com/jobs/view/1234567890",
    job_description="IT Support Analyst role...",
    user_id="your_user_id",
    user_info={"email": "your@email.com"},
    auto_apply=True
)

print(result)
```

---

## Applying to Multiple Jobs (Batch)

### Step 1: Prepare Your Job List

Create a file `jobs_to_apply.json`:

```json
[
    {
        "url": "https://linkedin.com/jobs/view/1111111111",
        "description": "Cybersecurity Analyst role requiring Python, Linux, and security tools."
    },
    {
        "url": "https://linkedin.com/jobs/view/2222222222",
        "description": "IT Support position with Windows, Azure, and networking experience."
    },
    {
        "url": "https://linkedin.com/jobs/view/3333333333",
        "description": "Cloud Engineer role with AWS and automation experience."
    }
]
```

### Step 2: Create Batch Application Script

Create `apply_batch.py`:

```python
import sys
import os
import json

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.services.job_application_orchestrator import apply_to_jobs_batch

# Load jobs from file
with open("jobs_to_apply.json", "r") as f:
    job_inputs = json.load(f)

# Your information
user_id = "your_user_id"
user_info = {
    "first_name": "Bryan",
    "last_name": "Ndum",
    "email": "bryanndum12@gmail.com"
}

print(f"🚀 Processing {len(job_inputs)} jobs...\n")

# Apply to all jobs
result = apply_to_jobs_batch(
    job_inputs=job_inputs,
    user_id=user_id,
    user_info=user_info,
    auto_apply=True,  # Set to True to actually apply
    min_score=65  # Minimum fit score to apply (0-100)
)

# Print summary
print("\n" + "="*60)
print("BATCH RESULTS SUMMARY")
print("="*60)
print(f"Total Jobs: {result.get('total_jobs')}")
print(f"Eligible Jobs (score >= 65): {result.get('eligible_jobs')}")
print(f"Applied: {result.get('applied')}")
print(f"Skipped (low score): {result.get('skipped')}")
print(f"Errors: {result.get('errors')}")

# Show individual results
print("\n" + "="*60)
print("INDIVIDUAL RESULTS")
print("="*60)
for i, job_result in enumerate(result.get('results', []), 1):
    print(f"\n{i}. {job_result.get('company', 'Unknown')} - {job_result.get('role', 'Unknown')}")
    print(f"   Fit Score: {job_result.get('fit_score', 0)}")
    print(f"   Status: {job_result.get('status')}")
    if job_result.get('status') == 'applied':
        print(f"   ✅ Application ID: {job_result.get('application_id')}")
```

**Run it:**
```bash
python apply_batch.py
```

---

## Using the API

### Step 1: Start the API Server

```bash
# From project root
cd app
uvicorn main:app --reload --port 8000
```

Or:
```bash
python -m uvicorn app.main:app --reload --port 8000
```

### Step 2: Apply via API

**Single Job:**
```bash
curl -X POST "http://localhost:8000/api/jobs/apply" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://linkedin.com/jobs/view/1234567890",
    "job_description": "IT Support Analyst role...",
    "user_id": "your_user_id",
    "user_info": {
      "email": "bryan@example.com",
      "first_name": "Bryan",
      "last_name": "Ndum"
    },
    "auto_apply": true
  }'
```

**Batch Jobs:**
```bash
curl -X POST "http://localhost:8000/api/jobs/apply/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "jobs": [
      {"url": "...", "description": "..."},
      {"url": "...", "description": "..."}
    ],
    "user_id": "your_user_id",
    "auto_apply": true,
    "min_score": 65
  }'
```

**Using Python requests:**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/jobs/apply",
    json={
        "url": "https://linkedin.com/jobs/view/1234567890",
        "job_description": "IT Support Analyst...",
        "user_id": "your_user_id",
        "user_info": {"email": "bryan@example.com"},
        "auto_apply": True
    }
)

print(response.json())
```

---

## Tracking Applications

### View Your Applications

```python
from app.services.callback_tracker import get_callback_statistics

stats = get_callback_statistics(user_id="your_user_id", days=30)

print(f"Total Applications: {stats.get('total_applications')}")
print(f"Callbacks: {stats.get('callbacks')}")
print(f"Interviews: {stats.get('interviews')}")
print(f"Callback Rate: {stats.get('callback_rate')}%")
print(f"Interview Rate: {stats.get('interview_rate')}%")
```

### Update Callback Status

```python
from app.services.callback_tracker import update_callback_status

# Mark application as having received a callback
update_callback_status(
    application_id="your_application_id",
    status="callback",  # Options: pending, callback, interview, rejected
    callback_date="2024-01-15T10:00:00",
    notes="Recruiter called to schedule interview"
)
```

### View in Supabase Dashboard

1. Go to: https://supabase.com/dashboard
2. Select your project
3. Go to: **Table Editor**
4. View the `applications` table to see all your applications

---

## Complete Workflow Example

Here's a complete example of applying to a job:

```python
import sys
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.services.job_application_orchestrator import apply_to_job

# Step 1: Define your information
user_id = "bryan_2024"
user_info = {
    "first_name": "Bryan",
    "last_name": "Ndum",
    "email": "bryanndum12@gmail.com",
    "phone": "+1-234-567-8900",
    "location": "Remote, NC",
    "linkedin": "https://linkedin.com/in/bryanndum"
}

# Step 2: Define the job
job_url = "https://www.linkedin.com/jobs/view/1234567890"
job_description = """
Senior IT Support Analyst

We are seeking a Senior IT Support Analyst to join our growing team.
You will be responsible for:
- Providing technical support for Windows and Linux systems
- Managing Azure cloud infrastructure
- Troubleshooting network issues
- Documenting solutions and processes

Requirements:
- 3+ years IT support experience
- Experience with Azure, Windows, Linux
- Strong troubleshooting skills
- Excellent communication skills
"""

# Step 3: Apply
print("🚀 Starting application process...\n")

result = apply_to_job(
    url=job_url,
    job_description=job_description,
    user_id=user_id,
    user_info=user_info,
    auto_apply=True  # Actually submit the application
)

# Step 4: Review results
print("\n" + "="*70)
print("APPLICATION RESULT")
print("="*70)

if result.get('status') == 'applied':
    print("✅ SUCCESS: Application submitted!")
    print(f"\nDetails:")
    print(f"  Company: {result.get('company')}")
    print(f"  Role: {result.get('role')}")
    print(f"  Fit Score: {result.get('fit_score')}/100")
    print(f"  Application ID: {result.get('application_id')}")
    
    if result.get('networking_message'):
        print(f"\n📧 Networking Message Generated:")
        print(f"  {result.get('networking_message', {}).get('message', '')[:200]}...")
        
elif result.get('status') == 'skipped':
    print(f"⏭️ SKIPPED: {result.get('reason')}")
    print(f"  Fit Score: {result.get('fit_score')}/100")
    
elif result.get('status') == 'ready_to_apply':
    print("📄 Resume and cover letter generated")
    print(f"  Resume: {result.get('resume_path')}")
    print(f"  Cover Letter: {result.get('cover_letter_path')}")
    print("\n⚠️ Set auto_apply=True to submit")
    
else:
    print(f"❌ ERROR: {result.get('error')}")

print("="*70)
```

---

## Understanding the Results

### Fit Score Ranges

- **80-100**: High fit - Priority apply
- **65-79**: Good fit - Apply at scale
- **< 65**: Low fit - Skipped automatically

### Status Values

- `applied`: Application successfully submitted
- `ready_to_apply`: Resume/cover letter generated, ready to apply
- `skipped`: Job didn't meet minimum fit score
- `error`: Something went wrong (check error message)

### What Happens During Auto-Apply

1. **Parse Job**: Extracts company, role, skills, etc.
2. **Score Fit**: Calculates 0-100 fit score
3. **Generate Resume**: Creates tailored resume PDF
4. **Generate Cover Letter**: Creates tailored cover letter
5. **Apply**: Opens browser, fills form, uploads files (80% automated)
6. **Track**: Saves application to database
7. **Network**: Generates LinkedIn follow-up message

**Note**: The system completes ~80% of the application. You may need to:
- Review and submit the final step
- Answer complex questions manually
- Handle any unexpected fields

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'playwright'"

**Solution:**
```bash
pip install playwright
python -m playwright install chromium
```

### Issue: "Missing Supabase environment variables"

**Solution:**
- Check your `.env` file exists in project root
- Verify variable names are correct (case-sensitive)
- Restart terminal/IDE after creating `.env`

### Issue: "Table does not exist"

**Solution:**
```bash
# Check which tables are missing
python Scripts/create_missing_tables.py

# Then run the SQL in Supabase SQL Editor
# (See create_networking_table.sql or database_setup.sql)
```

### Issue: "OpenAI API key invalid"

**Solution:**
- Verify key starts with `sk-`
- Check for extra spaces
- Ensure key hasn't expired
- Check OpenAI dashboard for usage limits

### Issue: Application fails during auto-apply

**Possible causes:**
- Website structure changed
- Captcha appeared (set `CAPTCHA_2CAPTCHA_API_KEY` if needed)
- Network timeout
- Required fields not found

**Solution:**
- Check the error message in results
- Try applying manually to see what's different
- Check browser console for errors
- Some ATS platforms may need manual completion

### Issue: Low callback rate

**Solution:**
- Review fit scores - only apply to jobs with score >= 65
- Check resume versions - use `get_optimal_resume_version()`
- Review callback statistics to see what works
- Adjust minimum score threshold

---

## Best Practices

### 1. Start Small
- Test with 1-2 jobs first
- Use `auto_apply=False` to generate resumes first
- Review generated materials before applying

### 2. Monitor Fit Scores
- Only apply to jobs with fit_score >= 65
- Focus on jobs with fit_score >= 80 for best results
- Review skipped jobs to understand why

### 3. Track Everything
- Update callback status regularly
- Review callback statistics weekly
- Identify patterns in successful applications

### 4. Optimize Over Time
- Use callback data to improve resume versions
- Adjust minimum score threshold based on results
- Focus on high-performing job types/companies

### 5. Quality Over Quantity
- Better to apply to 10 high-fit jobs than 100 low-fit jobs
- Customize for high-fit roles (score >= 80)
- Review applications before submitting

---

## Quick Reference

### Key Functions

```python
# Apply to single job
from app.services.job_application_orchestrator import apply_to_job
apply_to_job(url, job_description, user_id, user_info, auto_apply=True)

# Apply to multiple jobs
from app.services.job_application_orchestrator import apply_to_jobs_batch
apply_to_jobs_batch(job_inputs, user_id, user_info, auto_apply=True, min_score=65)

# Get callback statistics
from app.services.callback_tracker import get_callback_statistics
get_callback_statistics(user_id, days=30)

# Update callback status
from app.services.callback_tracker import update_callback_status
update_callback_status(application_id, status="callback")
```

### Important Files

- `apply_to_job.py` - Single job application script
- `apply_batch.py` - Batch application script
- `jobs_to_apply.json` - Job list for batch processing
- `.env` - API keys and configuration

### Useful Scripts

```bash
# Check Playwright installation
python Scripts/check_playwright.py

# Check database tables
python Scripts/create_missing_tables.py

# Test resume generation
python Tests/test_resume_pipeline.py

# Test full system
python Tests/test_job_application_system.py
```

---

## Next Steps

1. ✅ Set up your environment (API keys, database)
2. ✅ Test resume generation
3. ✅ Try applying to 1-2 jobs manually
4. ✅ Review results and optimize
5. ✅ Scale up to batch processing

**Need Help?**
- Check `SETUP_REQUIRED_KEYS.md` for API key setup
- Check `QUICK_DATABASE_SETUP.md` for database setup
- Check `SYSTEM_ARCHITECTURE.md` for system overview

---

**Happy Job Hunting! 🚀**






