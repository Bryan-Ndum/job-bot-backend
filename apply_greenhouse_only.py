"""
Fully Automated Greenhouse Job Application Script
Searches all sources, finds Greenhouse jobs, applies to ALL of them automatically
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

from app.services.job_discovery import JobDiscovery
from app.services.job_application_orchestrator import JobApplicationOrchestrator
from app.services.ats_detector import detect_ats
from app.services.user_profile import get_user_info, get_user_id

print("\n" + "="*70)
print("🌱 FULLY AUTOMATED GREENHOUSE JOB APPLICATIONS")
print("="*70 + "\n")
print("🎯 Mission: Find ALL Greenhouse jobs and apply to them automatically")
print("⚡ Fully automated - no manual intervention required")
print("="*70 + "\n")

# Configuration - Broad search to find any Greenhouse jobs
SEARCH_KEYWORDS = "entry level OR junior OR analyst OR specialist OR associate OR coordinator OR developer OR engineer"
LOCATION = ""  # Nationwide/Remote
JOB_SOURCES = ["indeed", "simplyhired", "linkedin", "glassdoor", "dice", "ziprecruiter"]
JOBS_PER_SOURCE = 50  # Get more jobs to find more Greenhouse

USER_ID = get_user_id()
USER_INFO = get_user_info()

EXCLUDE_KEYWORDS = [
    "senior", "sr.", "sr ", "principal", "lead", "manager", "director",
    "vp", "vice president", "executive", "ceo", "cto", "cfo",
    "10+ years", "8+ years", "7+ years", "6+ years", "5+ years experience",
    "security clearance", "secret clearance", "top secret", "ts/sci",
    "active clearance", "dod clearance", "government clearance", "clearance required",
    "must have clearance", "clearance eligibility", "eligible for clearance"
]

MIN_FIT_SCORE = 30  # Lower threshold to apply to more Greenhouse jobs

if __name__ == "__main__":
    discovery = JobDiscovery(headless=False)
    orchestrator = JobApplicationOrchestrator(USER_ID, USER_INFO)
    
    greenhouse_jobs = []
    all_jobs_found = []
    
    try:
        discovery.start()
        
        # Step 1: Discover jobs from all sources
        print("\n" + "="*70)
        print("🔍 STEP 1: DISCOVERING JOBS FROM ALL SOURCES")
        print("="*70 + "\n")
        
        for source in JOB_SOURCES:
            try:
                print(f"🔍 Searching {source.upper()}...")
                if source == "indeed":
                    jobs = discovery.search_indeed_jobs(SEARCH_KEYWORDS, LOCATION, limit=JOBS_PER_SOURCE)
                elif source == "simplyhired":
                    jobs = discovery.search_simplyhired_jobs(SEARCH_KEYWORDS, LOCATION, limit=JOBS_PER_SOURCE)
                elif source == "linkedin":
                    jobs = discovery.search_linkedin_jobs(SEARCH_KEYWORDS, LOCATION, limit=JOBS_PER_SOURCE)
                elif source == "glassdoor":
                    jobs = discovery.search_glassdoor_jobs(SEARCH_KEYWORDS, LOCATION, limit=JOBS_PER_SOURCE)
                elif source == "dice":
                    jobs = discovery.search_dice_jobs(SEARCH_KEYWORDS, LOCATION, limit=JOBS_PER_SOURCE)
                elif source == "ziprecruiter":
                    jobs = discovery.search_ziprecruiter_jobs(SEARCH_KEYWORDS, LOCATION, limit=JOBS_PER_SOURCE)
                elif source == "google":
                    jobs = discovery.search_google_jobs(SEARCH_KEYWORDS, LOCATION, limit=JOBS_PER_SOURCE)
                else:
                    continue
                
                all_jobs_found.extend(jobs)
                print(f"   ✅ Found {len(jobs)} jobs from {source}")
                time.sleep(1)  # Small delay between sources
            except Exception as e:
                print(f"   ⚠️ Error searching {source}: {e}")
                continue
        
        # Remove duplicates
        seen_urls = set()
        unique_jobs = []
        for job in all_jobs_found:
            url = job.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_jobs.append(job)
        
        print(f"\n📊 Total unique jobs found: {len(unique_jobs)}\n")
        
        # Step 2: Filter jobs
        print("="*70)
        print("📋 STEP 2: FILTERING JOBS")
        print("="*70 + "\n")
        
        filtered_jobs = discovery.filter_jobs(
            jobs=unique_jobs,
            exclude_keywords=EXCLUDE_KEYWORDS,
            include_keywords=None
        )
        
        print(f"✅ {len(filtered_jobs)} jobs passed filters\n")
        
        # Step 3: Detect Greenhouse jobs
        print("="*70)
        print("🌱 STEP 3: DETECTING GREENHOUSE JOBS")
        print("="*70 + "\n")
        
        from app.services.job_intake import parse_job_from_url
        
        greenhouse_urls = []
        for job in filtered_jobs:
            url = job.get("url", "")
            if not url:
                continue
            
            try:
                # Check URL for Greenhouse indicators
                if "greenhouse.io" in url.lower() or "gh_jid" in url.lower():
                    greenhouse_urls.append(url)
                    print(f"   ✅ Greenhouse job detected: {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
                    continue
                
                # Try to detect ATS type by checking the URL
                ats_type = detect_ats(url)
                if ats_type == "greenhouse":
                    greenhouse_urls.append(url)
                    print(f"   ✅ Greenhouse job detected: {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
            except Exception as e:
                # If detection fails, continue
                continue
        
        print(f"\n🌱 Found {len(greenhouse_urls)} Greenhouse jobs!\n")
        
        if len(greenhouse_urls) == 0:
            print("⚠️ No Greenhouse jobs found in this search.")
            print("\n💡 Tips to find more Greenhouse jobs:")
            print("   1. Try different search keywords")
            print("   2. Greenhouse is commonly used by tech companies")
            print("   3. Many startups and mid-size companies use Greenhouse")
            print("   4. The script will continue searching other sources...")
            print("\n⏭️ Continuing to search for Greenhouse jobs...\n")
        
        # Step 4: Apply to all Greenhouse jobs
        print("="*70)
        print(f"🚀 STEP 4: APPLYING TO {len(greenhouse_urls)} GREENHOUSE JOBS")
        print("="*70 + "\n")
        print("⚡ Fully automated - applications will proceed automatically\n")
        
        applied_count = 0
        skipped_count = 0
        error_count = 0
        
        for idx, url in enumerate(greenhouse_urls, 1):
            try:
                # Find job details
                job_details = None
                for job in filtered_jobs:
                    if job.get("url") == url:
                        job_details = job
                        break
                
                title = job_details.get("title", "N/A") if job_details else "N/A"
                company = job_details.get("company", "N/A") if job_details else "N/A"
                
                print(f"\n[{idx}/{len(greenhouse_urls)}] 🌱 GREENHOUSE: {title} at {company}")
                print(f"   URL: {url[:80]}...")
                
                # Apply to job
                result = orchestrator.process_job_url(
                    url=url,
                    job_description=job_details.get("description") if job_details else None,
                    auto_apply=True,
                    min_fit_score=MIN_FIT_SCORE
                )
                
                if result.get("status") == "applied":
                    applied_count += 1
                    print(f"   ✅ SUCCESSFULLY APPLIED (Fit: {result.get('fit_score', 0):.1f}/100)")
                elif result.get("status") == "skipped":
                    skipped_count += 1
                    print(f"   ⏭️ Skipped: {result.get('reason', 'Low fit score')}")
                else:
                    error_count += 1
                    print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
                
                # Wait between applications (3 seconds for speed)
                if idx < len(greenhouse_urls):
                    time.sleep(3)
                    
            except Exception as e:
                error_count += 1
                print(f"   ❌ Exception: {e}")
                continue
        
        # Final Summary
        print("\n" + "="*70)
        print("🎉 FINAL RESULTS - GREENHOUSE APPLICATIONS")
        print("="*70 + "\n")
        print(f"🌱 Greenhouse Jobs Found: {len(greenhouse_urls)}")
        print(f"✅ Successfully Applied: {applied_count}")
        print(f"⏭️ Skipped: {skipped_count}")
        print(f"❌ Errors: {error_count}")
        print("="*70 + "\n")
        
        if applied_count > 0:
            print(f"🎉 SUCCESS! Applied to {applied_count} Greenhouse jobs!")
        else:
            print("⚠️ No applications were successfully submitted.")
            print("   Check the errors above for details.")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Process interrupted by user")
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        discovery.stop()

