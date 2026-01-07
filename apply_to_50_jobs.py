"""
Apply to 50 Jobs - Will automatically detect and apply to Greenhouse jobs
"""

# Apply nest_asyncio FIRST before any other imports
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
from app.services.user_profile import get_user_info, get_user_id

print("\n" + "="*70)
print("🚀 APPLYING TO 50 JOBS")
print("="*70 + "\n")
print("ℹ️  This will search for jobs and apply to them.")
print("   The system will automatically detect Greenhouse jobs when applying.")
print("   We'll track how many Greenhouse jobs we find and apply to.\n")

# Configuration
SEARCH_KEYWORDS = "cybersecurity analyst OR information security OR security analyst"
LOCATION = ""  # Nationwide/Remote
JOB_SOURCES = ["indeed", "simplyhired", "google"]  # Sources that work best
JOBS_PER_SOURCE = 25

# User information
USER_ID = get_user_id()
USER_INFO = get_user_info()

EXCLUDE_KEYWORDS = [
    "senior", "sr.", "sr ", "principal", "lead", "manager", "director",
    "vp", "vice president", "executive", "ceo", "cto", "cfo",
    "10+ years", "8+ years", "5+ years experience",
    # Security clearance requirements
    "security clearance", "secret clearance", "top secret", "ts/sci", "ts/sci clearance",
    "active clearance", "dod clearance", "government clearance", "clearance required",
    "must have clearance", "clearance eligibility", "eligible for clearance"
]

MIN_FIT_SCORE = 40

print("⚙️ Configuration:")
print(f"   Keywords: {SEARCH_KEYWORDS}")
print(f"   Location: {LOCATION or 'Nationwide/Remote'}")
print(f"   Sources: {', '.join(JOB_SOURCES)}")
print(f"   Jobs per source: {JOBS_PER_SOURCE}")
print(f"   Target: Apply to 50 jobs")
print(f"   Min fit score: {MIN_FIT_SCORE}/100")
print()

if __name__ == "__main__":
    try:
        print("="*70)
        print("🔍 SEARCHING AND APPLYING TO JOBS")
        print("="*70 + "\n")
        print("This will search for jobs and automatically apply to them.")
        print("The system will detect Greenhouse jobs during the application process.\n")
        
        results = discover_and_apply(
            keywords=SEARCH_KEYWORDS,
            location=LOCATION,
            user_info=USER_INFO,
            user_id=USER_ID,
            sources=JOB_SOURCES,
            limit_per_source=JOBS_PER_SOURCE,
            exclude_keywords=EXCLUDE_KEYWORDS,
            include_keywords=None,
            min_fit_score=MIN_FIT_SCORE,
            auto_apply=True  # Actually apply
        )
        
        print("\n" + "="*70)
        print("📊 FINAL SUMMARY")
        print("="*70 + "\n")
        
        applied = results.get("applications_submitted", [])
        skipped = results.get("applications_skipped", [])
        errors = results.get("errors", [])
        
        print(f"✅ Successfully Applied: {len(applied)}")
        print(f"⏭️ Skipped: {len(skipped)}")
        print(f"❌ Errors: {len(errors)}")
        
        # Count Greenhouse jobs
        greenhouse_count = 0
        for app in applied:
            job = app.get("job", {})
            url = job.get("url", "")
            if url and ("greenhouse.io" in url.lower() or "gh_jid" in url.lower()):
                greenhouse_count += 1
        
        if greenhouse_count > 0:
            print(f"\n🌱 Greenhouse Jobs Applied: {greenhouse_count}")
        
        if len(applied) > 0:
            print(f"\n✅ Successfully applied to {len(applied)} jobs!")
            if greenhouse_count > 0:
                print(f"   ({greenhouse_count} were Greenhouse jobs)")
        
        print("="*70 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Process interrupted by user")
    except Exception as e:
        print(f"\n\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

