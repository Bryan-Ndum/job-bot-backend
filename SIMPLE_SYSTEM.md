# 🎯 Simple Job Application System

## Philosophy: Maximum Effectiveness, Minimum Complexity

This simplified system focuses on what actually works:
1. **Discover jobs** from job boards
2. **Filter** based on your criteria
3. **Score** jobs for fit
4. **Apply** automatically using one resume

**What we removed:**
- ❌ Complex AI resume generation (just use your good resume)
- ❌ Multiple datasets and resume variants
- ❌ Networking signal generation
- ❌ Complex tracking systems
- ❌ Unnecessary abstraction layers

**What we kept:**
- ✅ Fast job discovery from multiple sources
- ✅ Smart filtering (exclude senior roles, security clearance, etc.)
- ✅ Fit scoring (helps prioritize)
- ✅ Reliable auto-apply via Playwright
- ✅ Persistent login sessions
- ✅ Fast application speed (3 seconds between jobs)

---

## Quick Start

### Step 1: Place Your Resume

Put your resume PDF at:
```
storage/resumes/pdf/resume.pdf
```

That's it! The system will use this one resume for all applications.

### Step 2: Configure

Edit `apply_simple.py`:

```python
# Your information
USER_INFO = {
    "first_name": "Your Name",
    "last_name": "Your Last Name",
    "email": "your.email@example.com",
    "phone": "123-456-7890",
    "location": "Your City, State",
    "linkedin": "https://linkedin.com/in/yourprofile"
}

# Job search
SEARCH_KEYWORDS = "your keywords here"
LOCATION = ""  # Empty = nationwide/remote
JOB_SOURCES = ["indeed", "simplyhired"]
MIN_FIT_SCORE = 40  # Minimum score to apply (0-100)
```

### Step 3: Run

```bash
python apply_simple.py
```

That's it! The system will:
1. Search for jobs
2. Filter them
3. Score them
4. Apply automatically

---

## How It Works

### 1. Job Discovery
Searches multiple job boards (Indeed, SimplyHired, etc.) for jobs matching your keywords.

### 2. Filtering
Removes jobs with exclude keywords (senior roles, security clearance, etc.).

### 3. Fit Scoring
Scores each job 0-100 based on:
- Required skills match
- Tech stack alignment
- Location compatibility
- Seniority level

### 4. Application
For jobs with score >= min_fit_score:
- Opens job application page
- Fills your information
- Uploads your resume
- Submits application
- Waits 3 seconds before next job

---

## Files

- **`apply_simple.py`** - Main script to run
- **`app/services/simple_orchestrator.py`** - Simplified application logic
- **`app/services/simple_resume_service.py`** - Resume file management

---

## Tips

1. **Use one good resume** - Your best resume works for most jobs. No need to generate new ones.

2. **Adjust MIN_FIT_SCORE** - Start at 40, then increase if you want higher quality matches.

3. **Monitor the browser** - The system opens a visible browser so you can see what's happening.

4. **First time login** - You may need to log in to job boards the first time. The system saves your session.

5. **Speed** - Applications happen every 3 seconds. This is fast but not too fast (avoids detection).

---

## Troubleshooting

**Resume not found?**
- Make sure `storage/resumes/pdf/resume.pdf` exists
- Or set `RESUME_PATH` in the script

**Applications failing?**
- Check the browser window to see what's happening
- Some job boards may require manual login the first time
- Resume upload may fail on some sites - the system will continue to the next job

**No jobs found?**
- Try broader keywords
- Add more job sources (linkedin, glassdoor, dice)
- Check your location settings

---

## Comparison: Old vs Simple

| Feature | Old System | Simple System |
|---------|-----------|---------------|
| Resume | AI-generated, multiple variants | One good resume |
| Files | 7+ resume-related files | 2 simple files |
| Setup | Complex dataset setup | Just place resume PDF |
| Speed | Slower (generates resume per job) | Faster (uses existing resume) |
| Effectiveness | Same | Same (or better - uses your best resume) |

---

## When to Use Which

**Use Simple System (`apply_simple.py`) when:**
- ✅ You have a good resume already
- ✅ You want to apply quickly
- ✅ You want minimal setup
- ✅ You want maximum simplicity

**Use Full System (`apply_to_50_jobs.py`) when:**
- ✅ You want AI-tailored resumes per job
- ✅ You want networking follow-ups
- ✅ You want detailed tracking
- ✅ You're okay with more complexity

---

**Bottom line:** The simple system does 90% of the work with 10% of the complexity.



