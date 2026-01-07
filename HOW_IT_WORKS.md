# How the Job Discovery and Auto-Apply System Works

## 🎯 Overview

The system automatically:
1. **Discovers** jobs from multiple job boards (LinkedIn, Indeed, ZipRecruiter, Glassdoor, Dice, Built In)
2. **Filters** jobs based on your criteria (exclude senior roles, include keywords, etc.)
3. **Scores** each job for fit (0-100) using AI analysis
4. **Generates** tailored resumes and cover letters for each job
5. **Applies** automatically via browser automation
6. **Tracks** all applications in Supabase for callback optimization

---

## 📋 Step-by-Step Workflow

### Step 1: Job Discovery

The system opens a browser and searches each configured job board:

```
🔍 Searching LinkedIn jobs: cybersecurity analyst in North Carolina
   Found 25 job listings
   ✅ Collected 25 job URLs

🔍 Searching Indeed jobs: cybersecurity analyst in North Carolina
   Found 25 job listings
   ✅ Collected 25 job URLs

🔍 Searching ZipRecruiter jobs: cybersecurity analyst in North Carolina
   Found 25 job listings
   ✅ Collected 25 job URLs

📊 Total unique jobs found: 68 (after removing duplicates)
```

**What happens:**
- Opens browser (visible, not headless)
- Navigates to each job board's search URL
- Scrolls through results to load more jobs
- Extracts: job URL, title, company, location
- Removes duplicate jobs found across multiple boards

---

### Step 2: Filtering

Jobs are filtered based on your criteria:

```python
EXCLUDE_KEYWORDS = [
    "senior", "sr.", "principal", "lead", "manager", "director",
    "vp", "vice president", "10+ years", "8+ years"
]

INCLUDE_KEYWORDS = [
    # Optional: Only include jobs with these keywords
]
```

**Example:**
- Input: 68 jobs discovered
- Filters out jobs with "senior", "manager", "10+ years" in title/company
- Output: 45 jobs pass filtering

```
📋 Filtered jobs: 45/68 passed filters
```

---

### Step 3: Fit Scoring (AI Analysis)

Each job is analyzed by AI to calculate a fit score (0-100):

**Scoring Factors:**
- **Required skills overlap** (high weight) - How many required skills match your resume
- **Tech stack match** (high weight) - Technologies/tools you know
- **Resume keyword alignment** (medium) - How well your resume matches job keywords
- **Seniority alignment** (medium) - Entry-level vs senior expectations
- **Industry familiarity** (medium) - Experience in similar roles
- **Location compatibility** (medium) - Remote/local requirements

**Decision Rules:**
- Score >= 80 → Priority apply (high fit)
- Score 65-79 → Apply at scale with adaptation (good fit)
- Score < 65 → Skip (low fit)

**Example Output:**
```
[1/45] Processing: Junior Security Analyst at Varonis
   📊 Scoring job fit...
   Fit Score: 72/100
   Decision: apply
   Reason: Strong skill match in cybersecurity fundamentals
```

---

### Step 4: Resume & Cover Letter Generation

For jobs with fit score >= 65, the system generates tailored documents:

**Resume Adaptation:**
- Reorders skills to match job description
- Emphasizes relevant experience bullets
- Adds metrics to first bullets
- Selects best resume variant (general, IT, cybersecurity, etc.)

**Cover Letter Generation:**
- References the company/product/market
- Explains role alignment with your experience
- Mentions specific skills from job description
- Personalized closing

**Example:**
```
📄 Generating optimized resume and cover letter...
   ✅ Resume generated: outputs/resumes/job_abc123_resume.pdf
   ✅ Cover letter generated: outputs/cover_letters/job_abc123_cover.txt
```

---

### Step 5: Automated Application

The system opens the job application page and automatically fills it:

**Process:**
1. **Navigate** to job application URL
2. **Detect ATS** platform (Greenhouse, Lever, Workday, Jobvite, LinkedIn, etc.)
3. **Handle captcha** if present (using 2Captcha/Anti-Captcha)
4. **Fill personal info** (name, email, phone, location)
5. **Upload resume** (the tailored PDF)
6. **Upload cover letter** (if field available)
7. **Navigate multi-step forms** (click "Next" buttons)
8. **Handle EEO fields** (select "Prefer not to answer" for optional fields)
9. **Submit application** (click final submit button)

**Example:**
```
🤖 Starting automated application...
🌐 Navigating to https://jobs.jobvite.com/careers/varonis/job/abc123
🔎 Detected ATS: jobvite
✅ Modal captcha solved (hCaptcha)
📝 Processing Jobvite application form...
✏️ Filling personal information...
   ✅ Filled 4 fields
📤 Uploading resume...
   ✅ Resume uploaded
📄 Uploading cover letter...
   ✅ Cover letter uploaded
➡️ Navigating multi-step form...
   ✅ Clicked Next button
📋 Handling optional fields...
   ✅ EEO fields handled
🚀 Submitting application...
   ✅ Application submitted
```

---

### Step 6: Application Tracking

Each application is tracked in Supabase:

**Stored Information:**
```json
{
  "application_id": "uuid-here",
  "company": "Varonis",
  "role": "Junior Security Analyst",
  "fit_score": 72,
  "resume_version": "cybersecurity_variant",
  "cover_letter_version": "customized",
  "url": "https://jobs.jobvite.com/...",
  "date_applied": "2024-01-15",
  "callback_status": "pending",
  "user_id": "bryan_test"
}
```

**Networking Signal Generation:**
- Identifies recruiter/hiring manager via LinkedIn
- Generates personalized follow-up message
- Stores contact details for follow-up

---

## 🚀 Running the System

### Quick Start

1. **Configure** your search parameters in `discover_and_apply_jobs.py`:
   ```python
   SEARCH_KEYWORDS = "cybersecurity analyst"
   LOCATION = "North Carolina"
   JOB_SOURCES = ["linkedin", "indeed", "ziprecruiter", "glassdoor", "dice"]
   EXCLUDE_KEYWORDS = ["senior", "manager", "10+ years"]
   MIN_FIT_SCORE = 65
   ```

2. **Run** the script:
   ```bash
   python discover_and_apply_jobs.py
   ```

3. **Watch** the browser automatically:
   - Searches job boards
   - Filters jobs
   - Scores each job
   - Generates resumes/cover letters
   - Applies to matching jobs
   - Tracks everything

### Expected Output

```
======================================================================
🔍 AUTOMATED JOB DISCOVERY AND APPLICATION
======================================================================

⚙️ Configuration:
   Keywords: cybersecurity analyst
   Location: North Carolina
   Sources: linkedin, indeed, ziprecruiter, glassdoor, dice
   Jobs per source: 25
   Exclude keywords: senior, sr., sr , principal, lead...
   Min fit score: 65/100

======================================================================
🔍 JOB DISCOVERY
======================================================================

🔍 Searching LinkedIn jobs: cybersecurity analyst in North Carolina
   Found 25 job listings
   ✅ Collected 25 job URLs

🔍 Searching Indeed jobs: cybersecurity analyst in North Carolina
   Found 25 job listings
   ✅ Collected 25 job URLs

[... more boards ...]

📊 Total unique jobs found: 68

======================================================================
📋 FILTERING JOBS
======================================================================

📋 Filtered jobs: 45/68 passed filters

======================================================================
🚀 AUTO-APPLYING TO JOBS
======================================================================

[1/45] Processing: Junior Security Analyst at Varonis
   URL: https://jobs.jobvite.com/...
   📥 Parsing job from URL: ...
   📊 Scoring job fit...
   📄 Generating optimized resume and cover letter...
   🤖 Starting automated application...
   ✅ Application submitted (Fit: 72/100)
   ⏳ Waiting 10 seconds before next application...

[2/45] Processing: Security Analyst at TechCorp
   ...
   ⏭️ Skipped: Low fit score (Fit: 58/100)

[... continues for all jobs ...]

======================================================================
📊 DISCOVERY AND APPLICATION SUMMARY
======================================================================

Jobs Discovered: 68
Jobs After Filtering: 45
Applications Submitted: 23
Applications Skipped: 22
Errors: 0

✅ Successfully Applied To:
   - Junior Security Analyst at Varonis (Fit: 72/100)
   - Entry-Level Security Analyst at SecureCo (Fit: 68/100)
   [... more ...]

======================================================================
✅ JOB DISCOVERY AND APPLICATION COMPLETE
======================================================================
```

---

## ⚙️ Customization Options

### Search Parameters
- **Keywords**: Job search terms
- **Location**: Geographic filter
- **Sources**: Which job boards to search
- **Limit per source**: Max jobs per board (default: 25)

### Filtering
- **Exclude keywords**: Jobs with these terms are skipped
- **Include keywords**: Only jobs with these terms (optional)
- **Min fit score**: Minimum score to apply (default: 65)

### User Information
```python
USER_INFO = {
    "first_name": "Bryan",
    "last_name": "Ndum",
    "email": "bryanndum12@gmail.com",
    "phone": "",
    "location": "Morrisville, North Carolina",
    "linkedin": ""
}
```

---

## 🔒 Safety Features

1. **Rate Limiting**: 10 seconds between applications to avoid detection
2. **Fit Score Threshold**: Only applies to jobs with good match (>= 65)
3. **Error Handling**: Continues if one application fails
4. **Captcha Solving**: Automatically handles captchas when detected
5. **Duplicate Prevention**: Removes duplicate jobs across boards

---

## 📊 What Gets Tracked

All applications are stored in Supabase for analysis:

- Application ID (unique identifier)
- Company name
- Job title/role
- Fit score
- Resume version used
- Cover letter customization level
- Application URL
- Date applied
- Callback status (pending/interview/rejected)
- Networking contacts

**Use this data to:**
- See which resume versions get callbacks
- Identify high-performing job types
- Track application success rate
- Optimize resume/cover letter strategies

---

## 🎯 Best Practices

1. **Start Small**: Test with 1-2 job boards first
2. **Review Settings**: Check exclude/include keywords before running
3. **Monitor Browser**: Watch the automation to catch any issues
4. **Check Results**: Review applications in Supabase dashboard
5. **Iterate**: Adjust keywords/filters based on results
6. **Respect Rate Limits**: Don't run too frequently (once per day recommended)

---

## ❓ FAQ

**Q: How long does it take?**
A: Depends on number of jobs. ~30-60 seconds per application. 50 jobs = ~30-50 minutes.

**Q: Can I run it multiple times?**
A: Yes, but wait at least 1 day between runs to avoid being flagged.

**Q: What if a job requires manual steps?**
A: The system handles ~90% of applications automatically. If it encounters something unexpected, it will log an error and continue.

**Q: How do I know if applications were successful?**
A: Check the Supabase dashboard or review the console output. All applications are logged with status.

**Q: Can I customize the resume/cover letter more?**
A: Yes! Edit the templates in `app/services/resume_engine/templates/` and `datasets/cover_letter.json`.

---

## 🚨 Troubleshooting

**No jobs found:**
- Check keywords and location
- Try broader search terms
- Verify job boards are accessible

**All jobs skipped:**
- Lower MIN_FIT_SCORE
- Adjust EXCLUDE_KEYWORDS
- Check if keywords are too restrictive

**Browser errors:**
- Ensure Playwright/Chromium installed: `python -m playwright install chromium`
- Check internet connection
- Try headless=False to see what's happening

**Applications failing:**
- Check captcha API key is set
- Verify user info is correct
- Review error messages in console






