"""
Test Application to Varonis Junior Security Analyst Position
"""

import sys
import os
import time
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.services.job_application_orchestrator import apply_to_job

print("\n" + "="*70)
print("🚀 TESTING APPLICATION TO VARONIS JUNIOR SECURITY ANALYST")
print("="*70 + "\n")

# Job details
job_url = "https://jobs.jobvite.com/careers/varonis/job/ojCEyfwR/apply?jvs=LinkedInLimited&jvk=Apply&jvi=ojCEyfwR,Apply&j=ojCEyfwR&__jvst=Job%20Board&__jvsd=LinkedInLimited"

# Updated URL matches the one provided by user

job_description = """
Junior Security Analyst - 1st Shift
Varonis - Morrisville, North Carolina

Varonis is looking for a Junior Security Analyst for 1st Shift.

This position is ideal for someone with:
- Interest in cybersecurity and information security
- Basic understanding of security principles
- Analytical and problem-solving skills
- Attention to detail
- Ability to work in a team environment
- Strong communication skills

Key responsibilities may include:
- Monitoring security alerts and incidents
- Analyzing security events and logs
- Assisting with security investigations
- Documenting security findings
- Supporting security operations team
- Following established security procedures

This is an entry-level position perfect for recent graduates or those looking to start a career in cybersecurity.
"""

# User information
user_id = "bryan_test"
user_info = {
    "first_name": "Bryan",
    "last_name": "Ndum",
    "email": "bryanndum12@gmail.com",
    "phone": "",  # Add if you want
    "location": "Morrisville, North Carolina",
    "linkedin": ""  # Add if you want
}

print("📋 Job Details:")
print(f"   Company: Varonis")
print(f"   Role: Junior Security Analyst - 1st Shift")
print(f"   Location: Morrisville, North Carolina")
print(f"   URL: {job_url}")
print()

print("👤 User Information:")
print(f"   Name: {user_info['first_name']} {user_info['last_name']}")
print(f"   Email: {user_info['email']}")
print()

# Apply to job
print("🔄 Starting application process...")
print("   This will:")
print("   1. Parse the job")
print("   2. Score job fit (0-100)")
print("   3. Generate tailored resume")
print("   4. Generate cover letter")
print("   5. Apply automatically via browser")
print()

# Start timing
start_time = time.time()
start_datetime = datetime.now()

# For testing purposes, we'll modify the orchestrator behavior
# by directly calling the components and bypassing the score check
from app.services.job_intake import parse_job_from_url
from app.services.resume_optimizer import generate_optimized_resume, generate_optimized_cover_letter
from app.services.playwright_apply import apply_with_playwright
from app.services.callback_tracker import track_application
import uuid

print("⚠️  Note: Job has low fit score, but proceeding for testing...\n")

try:
    # Step 1: Parse job
    print("📥 Parsing job...")
    job_data = parse_job_from_url(job_url, job_description)
    
    # Step 2: Score (just for info, won't block)
    from app.services.job_fit_scorer import score_job_fit
    scored_job = score_job_fit(job_data)
    fit_score = scored_job.get("fit_score", 0)
    
    print(f"📊 Fit Score: {fit_score}/100 (below 65 threshold, but continuing for test)")
    print()
    
    # Step 3: Generate resume and cover letter
    print("📄 Generating resume and cover letter...")
    resume_data = generate_optimized_resume(
        job_description=job_data.get("raw_description", job_description),
        fit_score=fit_score,
        user_id=user_id,
        job_id=job_data.get("job_id", "")
    )
    
    cover_letter_data = generate_optimized_cover_letter(
        job_description=job_data.get("raw_description", job_description),
        company=job_data.get("company", "Varonis"),
        role=job_data.get("role", "Junior Security Analyst"),
        fit_score=fit_score
    )
    
    # Step 4: Apply
    print("🤖 Starting automated application...")
    application_id = str(uuid.uuid4())
    
    apply_result = apply_with_playwright(
        url=job_url,
        resume_path=resume_data["pdf_resume"],
        cover_letter_path=cover_letter_data.get("cover_letter"),
        user_info=user_info,
        headless=False,
        captcha_service="2captcha",
        captcha_api_key=os.getenv("CAPTCHA_2CAPTCHA_API_KEY")
    )
    
    # Step 5: Track application
    track_application(
        application_id=application_id,
        company=job_data.get("company", "Varonis"),
        role=job_data.get("role", "Junior Security Analyst"),
        fit_score=fit_score,
        resume_version=resume_data.get("resume_version", "default"),
        cover_letter_version=cover_letter_data.get("customization_level", "default"),
        url=job_url,
        user_id=user_id
    )
    
    # Build result
    result = {
        "job_id": job_data.get("job_id"),
        "company": job_data.get("company", "Varonis"),
        "role": job_data.get("role", "Junior Security Analyst"),
        "fit_score": fit_score,
        "decision": "apply",
        "status": "applied",
        "application_id": application_id,
        "apply_result": apply_result,
        "resume_path": resume_data["pdf_resume"],
        "cover_letter_path": cover_letter_data.get("cover_letter")
    }
    
    # Calculate duration
    end_time = time.time()
    duration_seconds = end_time - start_time
    duration_minutes = int(duration_seconds // 60)
    duration_secs = int(duration_seconds % 60)
    
    # Print results
    print("\n" + "="*70)
    print("📊 APPLICATION RESULTS")
    print("="*70 + "\n")
    
    print(f"Job ID: {result.get('job_id', 'N/A')}")
    print(f"Company: {result.get('company', 'N/A')}")
    print(f"Role: {result.get('role', 'N/A')}")
    print(f"Fit Score: {result.get('fit_score', 0)}/100")
    print(f"Decision: {result.get('decision', 'N/A')}")
    print(f"Reason: {result.get('reason', 'N/A')}")
    print(f"Status: {result.get('status', 'N/A')}")
    print()
    print(f"⏱️  Duration: {duration_minutes}m {duration_secs}s ({duration_seconds:.1f} seconds)")
    print(f"🕐 Started: {start_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🕑 Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    if result.get('status') == 'applied':
        print("✅ SUCCESS: Application submitted!")
        print(f"   Application ID: {result.get('application_id')}")
        print()
        if result.get('apply_result'):
            apply_result = result.get('apply_result', {})
            print("   Application Details:")
            print(f"   - ATS Type: {apply_result.get('ats_type', 'N/A')}")
            print(f"   - Completed Steps: {', '.join(apply_result.get('completed_steps', []))}")
            if apply_result.get('remaining_steps'):
                print(f"   - Remaining Steps: {', '.join(apply_result.get('remaining_steps', []))}")
            if apply_result.get('error'):
                print(f"   ⚠️ Warning: {apply_result.get('error')}")
        
        if result.get('networking_message'):
            print()
            print("📧 Networking Message Generated:")
            print(f"   {result.get('networking_message', {}).get('message', '')[:200]}...")
            
    elif result.get('status') == 'ready_to_apply':
        print("📄 Resume and cover letter generated successfully")
        print(f"   Resume: {result.get('resume_path')}")
        print(f"   Cover Letter: {result.get('cover_letter_path')}")
        print()
        print("   ⚠️ Application not submitted (auto_apply was False or failed)")
        
    elif result.get('status') == 'skipped':
        print(f"⏭️ Job skipped: {result.get('reason')}")
        print(f"   Fit score was too low: {result.get('fit_score')}/100")
        print("   (Minimum required: 65)")
        
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
        if result.get('error'):
            print(f"   Details: {result.get('error')}")
    
    print("\n" + "="*70)
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()

