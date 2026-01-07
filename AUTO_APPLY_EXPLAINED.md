# 🤖 How Auto-Apply Works

## Current Flow

The system **DOES** find jobs and submit applications automatically! Here's how:

### 1. Job Discovery ✅
- Searches multiple job boards (Google Jobs, Indeed, LinkedIn, etc.)
- Finds 50-200+ jobs based on your keywords

### 2. Job Filtering ✅
- Filters out jobs with exclude keywords (e.g., "senior", "manager")
- Keeps jobs with include keywords (if specified)
- **Note**: Fit score filtering happens later

### 3. Job Scoring & Application ✅
For each job:
- Parses the job description
- Scores job fit (0-100)
- **Checks if fit score >= min_fit_score** (default: 65)
- If score meets threshold:
  - ✅ Generates optimized resume
  - ✅ Generates tailored cover letter
  - ✅ **Automatically fills out application form**
  - ✅ **Uploads resume and cover letter**
  - ✅ **Submits the application**
  - ✅ Tracks in database
- If score too low:
  - ⏭️ Skips the job

---

## Why Jobs Might Be Skipped

Jobs are skipped if:
1. **Fit score too low** - Below your minimum threshold (default: 65/100)
2. **Application errors** - Form couldn't be filled, captcha issues, etc.
3. **Already applied** - Job URL already in database

---

## How to Apply to More Jobs

### Option 1: Lower Minimum Fit Score
In the web interface:
- Set "Minimum Fit Score" to **50** or **40** (lower threshold = more jobs)
- Jobs with lower scores will still be applied to

### Option 2: Set to 0 (Apply to Everything)
- Set "Minimum Fit Score" to **0**
- This will apply to ALL jobs found (not recommended, but possible)

### Option 3: Disable Fit Score Check (Advanced)
To truly apply to everything without any scoring:
- You'd need to modify the code to skip scoring
- Not recommended - fit score helps avoid wasting time on poor matches

---

## Recommended Settings

### For Maximum Applications
```
Minimum Fit Score: 50
Exclude Keywords: senior, sr., principal, lead, manager, director, 10+ years
```

### For Quality Applications (Recommended)
```
Minimum Fit Score: 65
Exclude Keywords: senior, sr., principal, lead, manager, director, vp, 10+ years, 8+ years
```

### For Maximum Coverage
```
Minimum Fit Score: 40
Exclude Keywords: (leave empty or minimal)
```

---

## What Happens When You Click "Start"

1. **Browser opens** (visible - you can watch!)
2. **Searches job boards** - You'll see it navigating
3. **For each job found**:
   - Opens job page
   - Fills out form automatically
   - Uploads resume/cover letter
   - Clicks submit
   - Moves to next job

**Total time**: 30-60 minutes for 50 jobs
- ~30-60 seconds per application
- 10 second delay between applications

---

## Troubleshooting

### "No applications submitted"
- **Check minimum fit score** - might be too high
- **Check exclude keywords** - might be filtering everything
- **Check job board** - LinkedIn requires login, try Google Jobs or Indeed

### "All jobs skipped"
- Lower the minimum fit score to 50 or 40
- Remove some exclude keywords
- Check terminal logs for specific reasons

### "Browser not opening"
- Make sure Playwright is installed: `python -m playwright install chromium`
- Check if another browser process is blocking

---

## Summary

**The system DOES find and apply automatically!** 

It's designed to:
- ✅ Find jobs from multiple sources
- ✅ Filter by keywords
- ✅ Score each job
- ✅ Apply to jobs meeting your threshold
- ✅ Skip low-quality matches

If you want more applications, **lower the minimum fit score** in the web interface!






