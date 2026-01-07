"""
Apply to 10 Jobs - Any Domain
Finds and applies to 10 good jobs across various domains
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
print("🔍 FINDING AND APPLYING TO 10 JOBS")
print("="*70 + "\n")

# Configuration - broad search to find various job types
SEARCH_KEYWORDS = "entry level OR junior OR analyst OR specialist OR associate OR coordinator"
LOCATION = ""  # Nationwide/Remote
JOB_SOURCES = ["indeed", "simplyhired", "linkedin", "glassdoor"]
JOBS_PER_SOURCE = 15  # Search more to find 10 good ones

USER_ID = get_user_id()
USER_INFO = get_user_info()

# Exclude senior/executive roles and security clearance requirements
EXCLUDE_KEYWORDS = [
    "senior", "sr.", "sr ", "principal", "lead", "manager", "director",
    "vp", "vice president", "executive", "ceo", "cto", "cfo",
    "10+ years", "8+ years", "7+ years", "6+ years", "5+ years experience",
    "security clearance", "secret clearance", "top secret", "ts/sci",
    "active clearance", "dod clearance", "government clearance", "clearance required",
    "must have clearance", "clearance eligibility", "eligible for clearance"
]

MIN_FIT_SCORE = 35  # Lower threshold to find more applicable jobs

print("⚙️ Configuration:")
print(f"   Keywords: {SEARCH_KEYWORDS}")
print(f"   Location: {LOCATION or 'Nationwide/Remote'}")
print(f"   Sources: {', '.join(JOB_SOURCES)}")
print(f"   Target: Apply to 10 jobs")
print(f"   Min fit score: {MIN_FIT_SCORE}/100")
print(f"   Excluding: senior roles, security clearance requirements")
print()

if __name__ == "__main__":
    try:
        print("="*70)
        print("🚀 STARTING JOB SEARCH AND APPLICATION")
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
            auto_apply=True,
            max_applications=10  # Stop after 10 successful applications
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
        
        if len(applied) > 0:
            print(f"\n🎉 Successfully applied to {len(applied)} job(s)!")
            print("\n📋 Jobs Applied To:")
            for idx, app in enumerate(applied, 1):
                job = app.get("job", {})
                title = job.get("title", "N/A")
                company = job.get("company", "N/A")
                score = app.get("fit_score", "N/A")
                status = app.get("status", "N/A")
                print(f"   {idx}. {title} at {company}")
                print(f"      Fit Score: {score}/100 | Status: {status}")
        else:
            print("\n⚠️ No applications were submitted.")
            print("   This could be due to:")
            print("   - Jobs not meeting minimum fit score")
            print("   - All jobs were duplicates")
            print("   - Application errors occurred")
            
            if len(skipped) > 0:
                print(f"\n   Skipped {len(skipped)} job(s) - check reasons above")
            if len(errors) > 0:
                print(f"\n   {len(errors)} error(s) occurred - check details above")
        
        print("\n" + "="*70)
        print("✅ PROCESS COMPLETE")
        print("="*70 + "\n")
        
        # Check database for final count
        try:
            from app.core.supabase_client import get_supabase
            supabase = get_supabase()
            result = supabase.table("applications").select("id", count="exact").eq("user_id", USER_ID).execute()
            total_count = result.count if hasattr(result, 'count') and result.count else (len(result.data) if result.data else 0)
            print(f"📊 Total applications in database: {total_count}")
        except:
            pass
        
        print()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Process interrupted by user")
    except Exception as e:
        print(f"\n\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

