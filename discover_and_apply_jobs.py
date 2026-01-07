"""
Discover Jobs Online and Apply Automatically
Main script to search job boards and apply to matching positions.
"""

# CRITICAL: Apply nest_asyncio FIRST before any other imports
# This allows Playwright sync API to work even if an event loop exists
try:
    import nest_asyncio
    nest_asyncio.apply()
except (ImportError, Exception):
    pass

import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.services.job_discovery import discover_and_apply

print("\n" + "="*70)
print("🔍 AUTOMATED JOB DISCOVERY AND APPLICATION")
print("="*70 + "\n")

# Configuration
SEARCH_KEYWORDS = "cybersecurity analyst"  # Job search keywords
LOCATION = "North Carolina"  # Location filter (empty string for anywhere)
JOB_SOURCES = ["linkedin", "indeed", "ziprecruiter", "glassdoor", "dice", "google", "monster", "simplyhired"]  # Job boards to search
# Available sources: linkedin, indeed, ziprecruiter, glassdoor, dice, builtin, google, monster, careerbuilder, simplyhired, angellist, remoteok, company:CompanyName
JOBS_PER_SOURCE = 25  # Maximum jobs to collect per source

# User information
USER_ID = "bryan_test"
USER_INFO = {
    "first_name": "Bryan",
    "last_name": "Ndum",
    "email": "bryanndum12@gmail.com",
    "phone": "984-274-7193",
    "location": "Clayton, North Carolina",
    "linkedin": "https://www.linkedin.com/in/bryan-ndum-99488b23a/"
}

# Filtering options
EXCLUDE_KEYWORDS = [
    "senior", "sr.", "sr ", "principal", "lead", "manager", "director",
    "vp", "vice president", "executive", "ceo", "cto", "cfo",
    "10+ years", "8+ years", "5+ years experience",
    # Security clearance requirements
    "security clearance", "secret clearance", "top secret", "ts/sci", "ts/sci clearance",
    "active clearance", "dod clearance", "government clearance", "clearance required",
    "must have clearance", "clearance eligibility", "eligible for clearance"
]

INCLUDE_KEYWORDS = [
    # Keywords that should be present (empty list = no requirement)
    # "entry", "junior", "associate", "cybersecurity", "security"
]

MIN_FIT_SCORE = 40  # Minimum fit score to apply (0-100)

# Execution
print("⚙️ Configuration:")
print(f"   Keywords: {SEARCH_KEYWORDS}")
print(f"   Location: {LOCATION or 'Anywhere'}")
print(f"   Sources: {', '.join(JOB_SOURCES)}")
print(f"   Jobs per source: {JOBS_PER_SOURCE}")
print(f"   Exclude keywords: {', '.join(EXCLUDE_KEYWORDS[:5])}...")
print(f"   Min fit score: {MIN_FIT_SCORE}/100")
print()

if __name__ == "__main__":
    try:
        results = discover_and_apply(
            keywords=SEARCH_KEYWORDS,
            location=LOCATION,
            user_info=USER_INFO,
            user_id=USER_ID,
            sources=JOB_SOURCES,
            limit_per_source=JOBS_PER_SOURCE,
            exclude_keywords=EXCLUDE_KEYWORDS,
            include_keywords=INCLUDE_KEYWORDS if INCLUDE_KEYWORDS else None,
            min_fit_score=MIN_FIT_SCORE,
            auto_apply=True
        )
        
        print("\n" + "="*70)
        print("✅ JOB DISCOVERY AND APPLICATION COMPLETE")
        print("="*70 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Process interrupted by user")
    except Exception as e:
        print(f"\n\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

