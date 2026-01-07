"""
Find 5 Best Greenhouse Jobs - Searches and scores Greenhouse jobs for fit
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
from app.services.ats_detector import detect_ats
from app.services.job_fit_scorer import score_job_fit

print("\n" + "="*70)
print("🔍 FINDING 5 BEST GREENHOUSE JOBS FOR YOU")
print("="*70 + "\n")

# Configuration - matching your profile (broader search to find more Greenhouse jobs)
SEARCH_KEYWORDS = "cybersecurity OR security analyst OR information security"
LOCATION = ""  # Nationwide/Remote
JOB_SOURCES = ["indeed", "simplyhired"]  # Focus on sources that work best
JOBS_PER_SOURCE = 50  # Search more to find Greenhouse jobs

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
print(f"   Sources: {', '.join(JOB_SOURCES)}")
print(f"   Jobs per source: {JOBS_PER_SOURCE}")
print(f"   Target: Find 5 best Greenhouse jobs")
print(f"   Min fit score: {MIN_FIT_SCORE}/100")
print()

if __name__ == "__main__":
    try:
        print("="*70)
        print("🔍 SEARCHING FOR JOBS")
        print("="*70 + "\n")
        print("Searching job boards to find Greenhouse jobs...\n")
        
        # Search for jobs (without applying)
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
            auto_apply=False  # Don't apply, just search
        )
        
        # Filter for Greenhouse jobs - use filtered jobs (already passed keyword filters)
        all_jobs = results.get("jobs_filtered", results.get("jobs_discovered", []))
        greenhouse_jobs = []
        
        print("\n" + "="*70)
        print("🌱 CHECKING JOBS FOR GREENHOUSE ATS")
        print("="*70 + "\n")
        print("Checking each job URL to detect if it uses Greenhouse...\n")
        
        from app.services.job_intake import parse_job_from_url
        
        for idx, job in enumerate(all_jobs, 1):
            url = job.get("url", "")
            if url:
                try:
                    # Parse job to detect ATS type (this will visit the URL)
                    print(f"[{idx}/{len(all_jobs)}] Checking: {job.get('title', 'N/A')[:50]}...")
                    job_data = parse_job_from_url(url)
                    ats = job_data.get("ats_type", detect_ats(url))
                    
                    if ats == "greenhouse":
                        # Merge parsed data with original job data
                        greenhouse_job = {**job, **job_data}
                        greenhouse_jobs.append(greenhouse_job)
                        print(f"   ✅ Found Greenhouse job: {job.get('title', 'N/A')}")
                except Exception as e:
                    # If parsing fails, still check URL pattern
                    ats = detect_ats(url)
                    if ats == "greenhouse":
                        greenhouse_jobs.append(job)
                        print(f"   ✅ Found Greenhouse job (from URL pattern): {job.get('title', 'N/A')}")
                    else:
                        print(f"   ⏭️ Not Greenhouse ({ats})")
        
        print(f"\n✅ Found {len(greenhouse_jobs)} Greenhouse jobs out of {len(all_jobs)} total jobs\n")
        
        if len(greenhouse_jobs) == 0:
            print("❌ No Greenhouse jobs found in this search.")
            print("   Greenhouse jobs may be less common in these search results.")
            print("   You might need to search specific companies or use different keywords.")
            sys.exit(0)
        
        # Score each Greenhouse job
        print("="*70)
        print("📊 SCORING JOBS FOR FIT")
        print("="*70 + "\n")
        
        scored_jobs = []
        for job in greenhouse_jobs:
            try:
                # Convert job to format expected by score_job_fit
                # If job was parsed, it should have the right structure already
                job_data_for_scoring = {
                    "job_id": job.get("job_id", ""),
                    "company": job.get("company", ""),
                    "role": job.get("role", job.get("title", "")),
                    "location": job.get("location", ""),
                    "required_skills": job.get("required_skills", []),
                    "preferred_skills": job.get("preferred_skills", []),
                    "tech_stack": job.get("tech_stack", []),
                    "seniority": job.get("seniority", "other"),
                    "keywords": job.get("keywords", []),
                    "raw_description": job.get("raw_description", job.get("description", ""))
                }
                
                # Score the job
                fit_result = score_job_fit(job_data_for_scoring)
                
                scored_jobs.append({
                    "job": job,
                    "fit_score": fit_result.get("fit_score", 0),
                    "decision": fit_result.get("decision", "unknown"),
                    "reasoning": fit_result.get("reason", "")
                })
            except Exception as e:
                print(f"   ⚠️ Error scoring job {job.get('title', 'N/A')}: {e}")
                continue
        
        # Sort by fit score (highest first)
        scored_jobs.sort(key=lambda x: x["fit_score"], reverse=True)
        
        # Get top 5
        top_5 = scored_jobs[:5]
        
        print("\n" + "="*70)
        print("🏆 TOP 5 GREENHOUSE JOBS FOR YOU")
        print("="*70 + "\n")
        
        for idx, scored_job in enumerate(top_5, 1):
            job = scored_job["job"]
            fit_score = scored_job["fit_score"]
            decision = scored_job["decision"]
            reasoning = scored_job.get("reasoning", "")
            
            print(f"\n{'='*70}")
            print(f"#{idx} - Fit Score: {fit_score}/100")
            print(f"{'='*70}")
            print(f"📌 Title: {job.get('title', 'N/A')}")
            print(f"🏢 Company: {job.get('company', 'N/A')}")
            print(f"📍 Location: {job.get('location', 'N/A')}")
            print(f"🔗 URL: {job.get('url', 'N/A')}")
            print(f"✅ Decision: {decision.upper()}")
            if reasoning:
                print(f"💡 Reasoning: {reasoning[:200]}..." if len(reasoning) > 200 else f"💡 Reasoning: {reasoning}")
            print()
        
        print("="*70)
        print("\n✅ Found 5 best Greenhouse jobs for you!")
        print("   You can now apply to these jobs using the application system.")
        print("="*70 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Process interrupted by user")
    except Exception as e:
        print(f"\n\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

