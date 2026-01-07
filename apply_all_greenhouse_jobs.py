"""
Fully Automated Greenhouse Job Application - Aggressive Search
Finds ALL Greenhouse jobs by visiting each job URL to detect the ATS
Then applies to ALL Greenhouse jobs automatically
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
from app.services.job_intake import parse_job_from_url

print("\n" + "="*70)
print("🌱 FULLY AUTOMATED GREENHOUSE JOB APPLICATIONS")
print("="*70 + "\n")
print("🎯 Mission: Find ALL Greenhouse jobs and apply automatically")
print("⚡ Aggressive search - visiting each job to detect Greenhouse")
print("="*70 + "\n")

# Configuration - BROAD SEARCH
SEARCH_KEYWORDS = "cybersecurity OR security OR network security OR IT security OR information security"
LOCATION = ""
JOB_SOURCES = ["indeed", "simplyhired"]  # Most reliable sources
JOBS_PER_SOURCE = 100  # Get many jobs

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
    "security clearance", "secret clearance", "top secret", "ts/sci",
    "active clearance", "dod clearance", "government clearance", "clearance required",
    "must have clearance", "clearance eligibility", "eligible for clearance"
]

MIN_FIT_SCORE = 30  # Low threshold to apply to more jobs

if __name__ == "__main__":
    discovery = JobDiscovery(headless=False)
    orchestrator = JobApplicationOrchestrator(USER_ID, USER_INFO)
    
    greenhouse_jobs = []
    
    try:
        discovery.start()
        
        # Step 1: Discover jobs
        print("\n" + "="*70)
        print("🔍 STEP 1: DISCOVERING JOBS")
        print("="*70 + "\n")
        
        all_jobs = []
        for source in JOB_SOURCES:
            try:
                print(f"🔍 Searching {source.upper()}...")
                if source == "indeed":
                    jobs = discovery.search_indeed_jobs(SEARCH_KEYWORDS, LOCATION, limit=JOBS_PER_SOURCE)
                elif source == "simplyhired":
                    jobs = discovery.search_simplyhired_jobs(SEARCH_KEYWORDS, LOCATION, limit=JOBS_PER_SOURCE)
                else:
                    continue
                
                all_jobs.extend(jobs)
                print(f"   ✅ Found {len(jobs)} jobs")
                time.sleep(1)
            except Exception as e:
                print(f"   ⚠️ Error: {e}")
        
        # Remove duplicates
        seen_urls = set()
        unique_jobs = []
        for job in all_jobs:
            url = job.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_jobs.append(job)
        
        print(f"\n📊 Total unique jobs: {len(unique_jobs)}\n")
        
        # Step 2: Filter
        print("="*70)
        print("📋 STEP 2: FILTERING JOBS")
        print("="*70 + "\n")
        
        filtered_jobs = discovery.filter_jobs(
            jobs=unique_jobs,
            exclude_keywords=EXCLUDE_KEYWORDS,
            include_keywords=None
        )
        
        print(f"✅ {len(filtered_jobs)} jobs after filtering\n")
        
        # Step 3: Detect Greenhouse by parsing each job
        print("="*70)
        print("🌱 STEP 3: DETECTING GREENHOUSE JOBS (parsing URLs)")
        print("="*70 + "\n")
        print("⏳ This may take a few minutes as we check each job URL...\n")
        
        greenhouse_urls = []
        
        for idx, job in enumerate(filtered_jobs, 1):
            url = job.get("url", "")
            if not url:
                continue
            
            try:
                # Check URL directly first (fast)
                if "greenhouse.io" in url.lower() or "gh_jid" in url.lower():
                    greenhouse_urls.append({
                        "url": url,
                        "title": job.get("title", "N/A"),
                        "company": job.get("company", "N/A")
                    })
                    print(f"   ✅ [{idx}/{len(filtered_jobs)}] Greenhouse detected: {job.get('title', 'N/A')[:50]}")
                    continue
                
                # Parse job to get application URL and detect ATS
                # This will follow redirects and get the actual application URL
                try:
                    job_data = parse_job_from_url(url)
                    application_url = job_data.get("application_url") or job_data.get("url") or url
                    
                    # Detect ATS from application URL
                    ats_type = detect_ats(application_url)
                    
                    if ats_type == "greenhouse":
                        greenhouse_urls.append({
                            "url": application_url,
                            "title": job_data.get("role") or job.get("title", "N/A"),
                            "company": job_data.get("company") or job.get("company", "N/A")
                        })
                        print(f"   ✅ [{idx}/{len(filtered_jobs)}] Greenhouse: {job_data.get('role', job.get('title', 'N/A'))[:50]}")
                
                except Exception as parse_error:
                    # If parsing fails, skip this job
                    if idx % 10 == 0:
                        print(f"   ⏳ [{idx}/{len(filtered_jobs)}] Processing...")
                    continue
                
                # Small delay to avoid overwhelming servers
                if idx % 5 == 0:
                    time.sleep(0.5)
                
            except Exception as e:
                continue
        
        print(f"\n🌱 Found {len(greenhouse_urls)} Greenhouse jobs!\n")
        
        if len(greenhouse_urls) == 0:
            print("⚠️ No Greenhouse jobs found in this search.")
            print("   Greenhouse jobs may be less common - trying direct application approach...\n")
            print("   Applying to all jobs and tracking which are Greenhouse...")
            # Fallback: apply to all and track Greenhouse
            greenhouse_urls = [{"url": job.get("url"), "title": job.get("title"), "company": job.get("company")} for job in filtered_jobs[:20]]
            print(f"   Will apply to first 20 jobs as fallback\n")
        
        # Step 4: Apply to all Greenhouse jobs
        print("="*70)
        print(f"🚀 STEP 4: APPLYING TO {len(greenhouse_urls)} JOBS")
        print("="*70 + "\n")
        
        applied_count = 0
        skipped_count = 0
        error_count = 0
        greenhouse_applied = 0
        
        for idx, job_info in enumerate(greenhouse_urls, 1):
            url = job_info.get("url")
            title = job_info.get("title", "N/A")
            company = job_info.get("company", "N/A")
            
            if not url:
                continue
            
            try:
                print(f"\n[{idx}/{len(greenhouse_urls)}] {title} at {company}")
                print(f"   URL: {url[:80]}...")
                
                # Apply
                result = orchestrator.process_job_url(
                    url=url,
                    job_description=None,
                    auto_apply=True,
                    min_fit_score=MIN_FIT_SCORE
                )
                
                # Check if this was actually a Greenhouse job
                is_greenhouse = "greenhouse.io" in url.lower() or "gh_jid" in url.lower()
                if not is_greenhouse:
                    # Try to detect from the result
                    apply_result = result.get("apply_result", {})
                    detected_ats = apply_result.get("ats_type", "")
                    is_greenhouse = detected_ats == "greenhouse"
                
                if result.get("status") == "applied":
                    applied_count += 1
                    if is_greenhouse:
                        greenhouse_applied += 1
                        print(f"   ✅ GREENHOUSE APPLICATION SUCCESS (Fit: {result.get('fit_score', 0):.1f}/100)")
                    else:
                        print(f"   ✅ Applied (Fit: {result.get('fit_score', 0):.1f}/100)")
                elif result.get("status") == "skipped":
                    skipped_count += 1
                    print(f"   ⏭️ Skipped: {result.get('reason', 'Low fit score')}")
                else:
                    error_count += 1
                    print(f"   ❌ Error: {result.get('error', 'Unknown')}")
                
                if idx < len(greenhouse_urls):
                    time.sleep(3)  # Wait between applications
                    
            except Exception as e:
                error_count += 1
                print(f"   ❌ Exception: {e}")
                continue
        
        # Final Summary
        print("\n" + "="*70)
        print("🎉 FINAL RESULTS")
        print("="*70 + "\n")
        print(f"🌱 Greenhouse Jobs Found: {len(greenhouse_urls)}")
        print(f"✅ Total Applied: {applied_count}")
        print(f"🌱 Greenhouse Applied: {greenhouse_applied}")
        print(f"⏭️ Skipped: {skipped_count}")
        print(f"❌ Errors: {error_count}")
        print("="*70 + "\n")
        
        if greenhouse_applied > 0:
            print(f"🎉 SUCCESS! Applied to {greenhouse_applied} Greenhouse jobs!")
        elif applied_count > 0:
            print(f"✅ Applied to {applied_count} jobs (some may be Greenhouse)")
        else:
            print("⚠️ No applications were successfully submitted.")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            discovery.stop()
        except:
            pass


