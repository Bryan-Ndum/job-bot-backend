# Job Discovery and Auto-Apply Guide

## Overview
The job discovery system automatically searches multiple job boards (LinkedIn, Indeed, ZipRecruiter, Glassdoor, Dice, Built In) and applies to matching positions based on your criteria and fit score.

## Quick Start

### Basic Usage

Run the main discovery script:
```bash
python discover_and_apply_jobs.py
```

### Configuration

Edit `discover_and_apply_jobs.py` to customize:

```python
# Search parameters
SEARCH_KEYWORDS = "cybersecurity analyst"  # Job search keywords
LOCATION = "North Carolina"  # Location filter (empty string for anywhere)
JOB_SOURCES = ["linkedin", "indeed", "ziprecruiter", "glassdoor", "dice"]  # Job boards to search
# Available sources: linkedin, indeed, ziprecruiter, glassdoor, dice, builtin
JOBS_PER_SOURCE = 25  # Maximum jobs to collect per source

# Filtering options
EXCLUDE_KEYWORDS = [
    "senior", "sr.", "principal", "lead", "manager", "director",
    "vp", "vice president", "executive", "10+ years", "8+ years"
]

INCLUDE_KEYWORDS = [
    # Optional: Keywords that must be present
    # "entry", "junior", "associate", "cybersecurity"
]

MIN_FIT_SCORE = 65  # Minimum fit score to apply (0-100)
```

## How It Works

1. **Job Discovery**: Searches multiple job boards (LinkedIn, Indeed, ZipRecruiter, Glassdoor, Dice, Built In) for jobs matching your keywords and location
2. **Filtering**: Removes jobs with exclude keywords and filters by include keywords
3. **Fit Scoring**: Each job is scored (0-100) based on:
   - Required skill overlap
   - Tech stack match
   - Seniority alignment
   - Location compatibility
4. **Auto-Application**: Automatically applies to jobs with fit score >= 65
5. **Tracking**: All applications are tracked in Supabase for callback optimization

## Programmatic Usage

You can also use the discovery module directly in your code:

```python
from app.services.job_discovery import discover_and_apply

results = discover_and_apply(
    keywords="cybersecurity analyst",
    location="North Carolina",
    user_info={
        "first_name": "Bryan",
        "last_name": "Ndum",
        "email": "bryanndum12@gmail.com",
        "phone": "",
        "location": "Morrisville, North Carolina"
    },
    user_id="bryan_test",
    sources=["linkedin", "indeed", "ziprecruiter", "glassdoor", "dice"],
    limit_per_source=25,
    exclude_keywords=["senior", "manager", "10+ years"],
    min_fit_score=65,
    auto_apply=True
)

print(f"Applications submitted: {len(results['applications_submitted'])}")
print(f"Applications skipped: {len(results['applications_skipped'])}")
```

## Discovery-Only Mode

To discover jobs without applying:

```python
from app.services.job_discovery import JobDiscovery

discovery = JobDiscovery(headless=False)
discovery.start()

# Search LinkedIn
linkedin_jobs = discovery.search_linkedin_jobs(
    keywords="cybersecurity analyst",
    location="North Carolina",
    limit=25
)

# Search Indeed
indeed_jobs = discovery.search_indeed_jobs(
    keywords="cybersecurity analyst",
    location="North Carolina",
    limit=25
)

# Search ZipRecruiter
ziprecruiter_jobs = discovery.search_ziprecruiter_jobs(
    keywords="cybersecurity analyst",
    location="North Carolina",
    limit=25
)

# Search Glassdoor
glassdoor_jobs = discovery.search_glassdoor_jobs(
    keywords="cybersecurity analyst",
    location="North Carolina",
    limit=25
)

# Search Dice (tech jobs)
dice_jobs = discovery.search_dice_jobs(
    keywords="cybersecurity analyst",
    location="North Carolina",
    limit=25
)

# Search Built In (tech startups)
builtin_jobs = discovery.search_builtin_jobs(
    keywords="cybersecurity analyst",
    location="New York",  # or "San Francisco", "Remote", etc.
    limit=25
)

# Filter jobs
all_jobs = linkedin_jobs + indeed_jobs + ziprecruiter_jobs + glassdoor_jobs + dice_jobs + builtin_jobs
filtered = discovery.filter_jobs(
    jobs=all_jobs,
    exclude_keywords=["senior", "manager"],
    include_keywords=["entry", "junior"]
)

discovery.stop()
```

## Available Job Boards

1. **Google Jobs** - `"google"` - Aggregates from multiple sources (RECOMMENDED!)
2. **Indeed** - `"indeed"` - Largest job aggregator
3. **LinkedIn** - `"linkedin"` - Professional network job board (requires login)
4. **ZipRecruiter** - `"ziprecruiter"` - Major job board
5. **Glassdoor** - `"glassdoor"` - Jobs with company reviews
6. **Dice** - `"dice"` - Tech-focused job board
7. **Monster** - `"monster"` - Major job board
8. **SimplyHired** - `"simplyhired"` - Job aggregator
9. **CareerBuilder** - `"careerbuilder"` - Major job board
10. **AngelList/Wellfound** - `"angellist"` - Startup jobs
11. **RemoteOK** - `"remoteok"` - Remote jobs only
12. **Built In** - `"builtin"` - Tech startup jobs (supports: NYC, SF, Austin, Chicago, Boston, Seattle, LA, Remote)
13. **Company Websites** - `"company:CompanyName"` - Search specific company careers pages (e.g., `"company:Microsoft"`, `"company:Google"`)

### Recommended Setup

For maximum job discovery, use:
```python
sources = ["google", "indeed", "ziprecruiter", "simplyhired", "monster"]
```

Google Jobs is highly recommended as it aggregates from many sources!

## Results Structure

The `discover_and_apply` function returns:

```python
{
    "jobs_discovered": [...],  # All jobs found
    "jobs_filtered": [...],    # Jobs after filtering
    "applications_submitted": [
        {
            "job": {...},
            "application_id": "...",
            "fit_score": 75
        }
    ],
    "applications_skipped": [
        {
            "job": {...},
            "reason": "Low fit score",
            "fit_score": 45
        }
    ],
    "errors": [...]
}
```

## Notes

- **Rate Limiting**: The system waits 10 seconds between applications to avoid being blocked
- **Browser Mode**: Discovery runs in headful mode (visible browser) by default
- **LinkedIn/Indeed Access**: May require logging in if you hit rate limits
- **Fit Score Threshold**: Jobs below the minimum fit score are automatically skipped
- **Captcha Handling**: Automatically handles captchas when detected

## Troubleshooting

1. **No jobs found**: Check your keywords and location settings
2. **All jobs skipped**: Lower the `MIN_FIT_SCORE` or adjust `EXCLUDE_KEYWORDS`
3. **Browser errors**: Ensure Playwright and Chromium are installed (`python -m playwright install chromium`)
4. **Rate limiting**: Reduce `JOBS_PER_SOURCE` or add delays between searches

