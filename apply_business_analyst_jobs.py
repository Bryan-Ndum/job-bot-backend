"""
Apply to Business Analyst Jobs - Fully Automated
"""

# Apply nest_asyncio FIRST
try:
    import nest_asyncio
    nest_asyncio.apply()
except:
    pass

import sys
import os
import time

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
print("📊 APPLYING TO BUSINESS ANALYST JOBS")
print("="*70 + "\n")

# Configuration
SEARCH_KEYWORDS = "business analyst OR business analysis OR data analyst OR systems analyst OR financial analyst"
LOCATION = ""  # Nationwide/Remote
JOB_SOURCES = ["indeed", "simplyhired", "linkedin", "glassdoor", "dice"]
JOBS_PER_SOURCE = 50

USER_ID = get_user_id()
USER_INFO = get_user_info()  # Defaults to Clayton; set JOBBOT_ADDRESS=pembroke to switch

EXCLUDE_KEYWORDS = [
    "senior", "sr.", "sr ", "principal", "lead", "manager", "director",
    "vp", "vice president", "executive", "ceo", "cto", "cfo",
    "10+ years", "8+ years", "5+ years experience",
    "security clearance", "secret clearance", "top secret", "ts/sci",
    "active clearance", "dod clearance", "government clearance", "clearance required",
    "must have clearance", "clearance eligibility", "eligible for clearance"
]

MIN_FIT_SCORE = 40  # Lower threshold to apply to more business analyst roles

print("⚙️ Configuration:")
print(f"   Keywords: {SEARCH_KEYWORDS}")
print(f"   Location: {LOCATION or 'Nationwide/Remote'}")
print(f"   Sources: {', '.join(JOB_SOURCES)}")
print(f"   Jobs per source: {JOBS_PER_SOURCE}")
print(f"   Min fit score: {MIN_FIT_SCORE}/100")
print()

if __name__ == "__main__":
    try:
        print("="*70)
        print("🔍 SEARCHING AND APPLYING TO BUSINESS ANALYST JOBS")
        print("="*70 + "\n")
        
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
            auto_apply=True
        )
        
        print("\n" + "="*70)
        print("📊 FINAL SUMMARY - BUSINESS ANALYST APPLICATIONS")
        print("="*70 + "\n")
        
        applied = results.get("applications_submitted", [])
        skipped = results.get("applications_skipped", [])
        errors = results.get("errors", [])
        
        print(f"✅ Successfully Applied: {len(applied)}")
        print(f"⏭️ Skipped: {len(skipped)}")
        print(f"❌ Errors: {len(errors)}")
        
        if len(applied) > 0:
            print(f"\n✅ Successfully applied to {len(applied)} business analyst jobs!")
            print("\n📋 Jobs Applied To:")
            for idx, app in enumerate(applied[:20], 1):  # Show first 20
                job = app.get("job", {})
                print(f"   {idx}. {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
            if len(applied) > 20:
                print(f"   ... and {len(applied) - 20} more")
        
        print("="*70 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Process interrupted by user")
    except Exception as e:
        print(f"\n\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


