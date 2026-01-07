"""
Simple Job Application Script
Just run this to apply to jobs - no complexity, just results
"""

# Apply nest_asyncio FIRST
try:
    import nest_asyncio
    nest_asyncio.apply()
except:
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
from app.services.simple_orchestrator import apply_to_job_simple

print("\n" + "="*70)
print("🚀 SIMPLE JOB APPLICATION SYSTEM")
print("="*70 + "\n")

# ============================================================================
# CONFIGURATION - Edit these for your needs
# ============================================================================

# Your information
USER_INFO = {
    "first_name": "Bryan",
    "last_name": "Ndum",
    "email": "bryanndum12@gmail.com",
    "phone": "984-274-7193",
    "location": "Clayton, North Carolina",
    "linkedin": "https://www.linkedin.com/in/bryan-ndum-99488b23a/"
}

# Job search settings
SEARCH_KEYWORDS = "cybersecurity analyst OR information security OR security analyst"
LOCATION = ""  # Empty = nationwide/remote
JOB_SOURCES = ["indeed", "simplyhired"]  # Fast, reliable sources
JOBS_PER_SOURCE = 25
MIN_FIT_SCORE = 40  # Minimum score to apply (0-100)

# Resume (uses default: storage/resumes/pdf/resume.pdf)
# To use a different resume, uncomment and set:
# RESUME_PATH = "path/to/your/resume.pdf"

# Keywords to exclude
EXCLUDE_KEYWORDS = [
    "senior", "sr.", "sr ", "principal", "lead", "manager", "director",
    "vp", "vice president", "executive", "ceo", "cto", "cfo",
    "10+ years", "8+ years", "5+ years experience",
    # Security clearance
    "security clearance", "secret clearance", "top secret", "ts/sci",
    "active clearance", "dod clearance", "government clearance",
    "clearance required", "must have clearance"
]

# ============================================================================
# MAIN - Just run this script
# ============================================================================

if __name__ == "__main__":
    try:
        print("⚙️ Configuration:")
        print(f"   Keywords: {SEARCH_KEYWORDS}")
        print(f"   Location: {LOCATION or 'Nationwide/Remote'}")
        print(f"   Sources: {', '.join(JOB_SOURCES)}")
        print(f"   Jobs per source: {JOBS_PER_SOURCE}")
        print(f"   Min fit score: {MIN_FIT_SCORE}/100")
        print()
        
        # Check resume exists
        from app.services.simple_resume_service import get_resume_path
        try:
            resume_path = get_resume_path()
            print(f"✅ Resume found: {resume_path}")
        except FileNotFoundError as e:
            print(f"❌ {e}")
            print("\nPlease place your resume PDF at: storage/resumes/pdf/resume.pdf")
            sys.exit(1)
        
        print("\n" + "="*70)
        print("🔍 SEARCHING AND APPLYING TO JOBS")
        print("="*70 + "\n")
        
        # Use the existing discover_and_apply but with simplified orchestrator
        # For now, we'll modify it to use simple orchestrator
        # Actually, let's create a wrapper that uses the simple orchestrator
        
        from app.services.job_discovery import JobDiscovery
        
        discovery = JobDiscovery(headless=False)
        discovery.start()
        
        try:
            # Step 1: Discover jobs
            print("🔍 Discovering jobs...\n")
            jobs = discovery.search_jobs(
                keywords=SEARCH_KEYWORDS,
                location=LOCATION,
                sources=JOB_SOURCES,
                limit_per_source=JOBS_PER_SOURCE
            )
            
            print(f"\n📊 Found {len(jobs)} jobs\n")
            
            # Step 2: Filter jobs
            print("📋 Filtering jobs...\n")
            filtered_jobs = discovery.filter_jobs(
                jobs=jobs,
                exclude_keywords=EXCLUDE_KEYWORDS,
                include_keywords=None
            )
            
            print(f"✅ {len(filtered_jobs)} jobs passed filters\n")
            
            # Step 3: Apply to jobs
            if filtered_jobs:
                print("="*70)
                print("🚀 APPLYING TO JOBS")
                print("="*70 + "\n")
                
                applied_count = 0
                skipped_count = 0
                error_count = 0
                
                for idx, job in enumerate(filtered_jobs, 1):
                    url = job.get("url", "")
                    if not url:
                        continue
                    
                    print(f"\n[{idx}/{len(filtered_jobs)}] {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
                    
                    result = apply_to_job_simple(
                        url=url,
                        job_description=job.get("description"),
                        user_info=USER_INFO,
                        min_fit_score=MIN_FIT_SCORE,
                        auto_apply=True
                    )
                    
                    if result["status"] == "applied":
                        applied_count += 1
                        print(f"   ✅ Applied (Fit: {result['fit_score']:.1f}/100)")
                    elif result["status"] == "skipped":
                        skipped_count += 1
                        print(f"   ⏭️ Skipped: {result.get('reason', 'Low fit score')}")
                    else:
                        error_count += 1
                        print(f"   ❌ Error: {result.get('error', 'Unknown')}")
                    
                    # Wait between applications (3 seconds for speed)
                    if idx < len(filtered_jobs):
                        import time
                        time.sleep(3)
                
                # Summary
                print("\n" + "="*70)
                print("📊 FINAL SUMMARY")
                print("="*70 + "\n")
                print(f"✅ Applied: {applied_count}")
                print(f"⏭️ Skipped: {skipped_count}")
                print(f"❌ Errors: {error_count}")
                print("="*70 + "\n")
            else:
                print("❌ No jobs found after filtering")
        
        finally:
            discovery.stop()
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()



