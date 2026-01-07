"""
Find and Apply to 50 Greenhouse Jobs from Multiple Sources
Searches multiple job boards and filters for Greenhouse jobs
"""

# Apply nest_asyncio FIRST before any other imports
try:
    import nest_asyncio
    nest_asyncio.apply()
except (ImportError, Exception):
    pass

import sys
import os
import re

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.services.job_discovery import discover_and_apply

def is_greenhouse_url(url: str) -> bool:
    """Check if URL is a Greenhouse job posting."""
    if not url:
        return False
    url_lower = url.lower()
    # Check for Greenhouse domain
    if "greenhouse.io" in url_lower or "boards.greenhouse.io" in url_lower:
        return True
    # Check for gh_jid parameter (Greenhouse job ID pattern)
    if re.search(r"gh_jid", url_lower):
        return True
    return False

print("\n" + "="*70)
print("🌱 FINDING AND APPLYING TO 50 GREENHOUSE JOBS")
print("="*70 + "\n")
print("ℹ️  Searching multiple job boards and filtering for Greenhouse jobs")
print("   Focus: Greenhouse ATS jobs (greenhouse.io or gh_jid parameter)\n")

# Configuration - Search broadly across multiple sources
SEARCH_KEYWORDS = "cybersecurity analyst OR information security OR security analyst OR security engineer"
LOCATION = ""  # Nationwide/Remote for more results
# Search multiple sources (not just Indeed)
JOB_SOURCES = [
    "google",      # Google Jobs aggregates from many sources
    "indeed",      # Indeed
    "simplyhired", # SimplyHired
    "linkedin",    # LinkedIn
    "glassdoor",   # Glassdoor
    "ziprecruiter", # ZipRecruiter
    "dice",        # Dice (tech jobs)
    "monster"      # Monster
]
JOBS_PER_SOURCE = 50  # Get many jobs per source to find Greenhouse ones

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
print(f"   Sources: {', '.join(JOB_SOURCES)} ({len(JOB_SOURCES)} sources)")
print(f"   Jobs per source: {JOBS_PER_SOURCE}")
print(f"   Target: 50 Greenhouse jobs")
print(f"   Min fit score: {MIN_FIT_SCORE}/100")
print()

if __name__ == "__main__":
    try:
        print("="*70)
        print("STEP 1: DISCOVERING JOBS FROM ALL SOURCES")
        print("="*70 + "\n")
        
        # First, discover jobs (don't apply yet)
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
            auto_apply=False  # Just discover first
        )
        
        all_jobs = results.get("jobs_discovered", [])
        print(f"\n✅ Discovered {len(all_jobs)} total jobs from all sources")
        
        # Filter for Greenhouse jobs
        print("\n" + "="*70)
        print("STEP 2: FILTERING FOR GREENHOUSE JOBS")
        print("="*70 + "\n")
        
        greenhouse_jobs = []
        for job in all_jobs:
            url = job.get("url", "")
            if url and is_greenhouse_url(url):
                greenhouse_jobs.append(job)
                print(f"   ✅ Found Greenhouse job: {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
        
        print(f"\n✅ Found {len(greenhouse_jobs)} Greenhouse jobs")
        
        if len(greenhouse_jobs) == 0:
            print("\n❌ No Greenhouse jobs found in search results.")
            print("\n💡 This is common because job boards often redirect to their own application pages.")
            print("   Greenhouse jobs are typically found:")
            print("   1. On company career pages directly")
            print("   2. Through direct Greenhouse URLs")
            print("   3. When job boards link directly to company pages (less common)")
            print("\n🔧 Let's try applying to the jobs we found anyway - some may redirect to Greenhouse.")
            print("   Or you can manually add Greenhouse job URLs.\n")
            
            print("\n⚠️  Since no Greenhouse URLs found in search results,")
            print("   we'll apply to all found jobs and the system will detect Greenhouse during application.")
            print("   Some jobs may redirect to Greenhouse when you apply.\n")
            
            # Apply to all jobs, system will detect Greenhouse during application
            print("="*70)
            print("STEP 3: APPLYING TO JOBS (System will detect Greenhouse during application)")
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
            
            # Count Greenhouse jobs from results
            applied = results.get("applications_submitted", [])
            greenhouse_count = 0
            for app in applied:
                result = app.get("result", {})
                if result.get("ats_type") == "greenhouse":
                    greenhouse_count += 1
            
            print("\n" + "="*70)
            print("📊 FINAL SUMMARY")
            print("="*70 + "\n")
            print(f"✅ Total Applied: {len(applied)}")
            print(f"🌱 Greenhouse Jobs Applied: {greenhouse_count}")
            print("="*70 + "\n")
        else:
            # Limit to 50 Greenhouse jobs
            greenhouse_jobs = greenhouse_jobs[:50]
            print(f"📋 Will apply to {len(greenhouse_jobs)} Greenhouse jobs\n")
            
            # Now apply to Greenhouse jobs
            print("="*70)
            print("STEP 3: APPLYING TO GREENHOUSE JOBS")
            print("="*70 + "\n")
            
            from app.services.job_application_orchestrator import JobApplicationOrchestrator
            
            orchestrator = JobApplicationOrchestrator(USER_ID, USER_INFO)
            
            applied_count = 0
            skipped_count = 0
            error_count = 0
            
            for i, job in enumerate(greenhouse_jobs, 1):
                url = job.get("url", "")
                title = job.get("title", "N/A")
                company = job.get("company", "N/A")
                
                print(f"\n{'='*70}")
                print(f"🌱 GREENHOUSE JOB {i}/{len(greenhouse_jobs)}")
                print(f"{'='*70}")
                print(f"Title: {title}")
                print(f"Company: {company}")
                print(f"URL: {url[:100]}...")
                print()
                
                try:
                    result = orchestrator.process_job_url(
                        url=url,
                        job_description=job.get("description"),
                        auto_apply=True,
                        min_fit_score=MIN_FIT_SCORE
                    )
                    
                    if result.get("status") == "applied":
                        applied_count += 1
                        print(f"✅ Successfully applied! ({applied_count}/{len(greenhouse_jobs)})")
                        if result.get("application_id"):
                            print(f"   Application ID: {result.get('application_id')}")
                        if result.get("ats_type") == "greenhouse":
                            print(f"   ✅ Confirmed Greenhouse ATS")
                    elif result.get("status") == "skipped":
                        skipped_count += 1
                        print(f"⏭️ Skipped: {result.get('reason', 'Unknown')} ({skipped_count} skipped)")
                    else:
                        error_count += 1
                        print(f"❌ Error: {result.get('error', 'Unknown error')} ({error_count} errors)")
                    
                    # Wait between applications to avoid rate limiting (reduced for speed)
                    if i < len(greenhouse_jobs):
                        wait_time = 3  # 3 seconds between applications (reduced from 10)
                        print(f"\n⏳ Waiting {wait_time} seconds before next application...")
                        import time
                        time.sleep(wait_time)
                        
                except Exception as e:
                    error_count += 1
                    error_msg = str(e)
                    print(f"❌ Exception: {error_msg} ({error_count} errors)")
                    import traceback
                    traceback.print_exc()
            
            # Final Summary
            print("\n" + "="*70)
            print("📊 FINAL SUMMARY")
            print("="*70 + "\n")
            
            print(f"🌱 Greenhouse Jobs Found: {len(greenhouse_jobs)}")
            print(f"✅ Successfully Applied: {applied_count}/{len(greenhouse_jobs)}")
            print(f"⏭️ Skipped: {skipped_count}/{len(greenhouse_jobs)}")
            print(f"❌ Errors: {error_count}/{len(greenhouse_jobs)}")
            
            if applied_count > 0:
                print(f"\n🎉 Successfully applied to {applied_count} Greenhouse jobs!")
        
        print("="*70 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Process interrupted by user")
    except Exception as e:
        print(f"\n\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

