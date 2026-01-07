"""
Apply to specific SIG job
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

from app.services.job_application_orchestrator import JobApplicationOrchestrator
from app.services.user_profile import get_user_info, get_user_id

print("\n" + "="*70)
print("🎯 APPLYING TO SIG JOB")
print("="*70 + "\n")

# Job URL
JOB_URL = "https://careers.sig.com/apply?jobSeqNo=SUSQA004Y9201&mode=apply&iis=LinkedIn"

# User info
USER_ID = get_user_id()
USER_INFO = get_user_info()

print(f"📍 Job URL: {JOB_URL}")
print(f"👤 Applicant: {USER_INFO['first_name']} {USER_INFO['last_name']}")
print()

if __name__ == "__main__":
    try:
        # Detect ATS type
        from app.services.ats_detector import detect_ats
        ats_type = detect_ats(JOB_URL)
        print(f"🔍 Detected ATS: {ats_type}\n")
        
        # Create orchestrator
        orchestrator = JobApplicationOrchestrator(USER_ID, USER_INFO)
        
        print("="*70)
        print("🚀 STARTING APPLICATION PROCESS")
        print("="*70 + "\n")
        
        # Apply to job with a lower threshold
        result = orchestrator.process_job_url(
            url=JOB_URL,
            job_description=None,  # Will be parsed from the page
            auto_apply=True,
            min_fit_score=30  # Lower threshold
        )
        
        # Display results
        print("\n" + "="*70)
        print("📊 APPLICATION RESULT")
        print("="*70 + "\n")
        
        status = result.get("status", "unknown")
        fit_score = result.get("fit_score", 0)
        company = result.get("company", "SIG")
        role = result.get("role", "Unknown")
        
        print(f"Company: {company}")
        print(f"Role: {role}")
        print(f"Fit Score: {fit_score}/100")
        print(f"Status: {status}")
        
        if status == "applied":
            print("\n✅ APPLICATION SUCCESSFULLY SUBMITTED!")
            print(f"   Application ID: {result.get('application_id', 'N/A')}")
            print(f"   Duration: {result.get('duration', 'N/A')}")
        elif status == "duplicate":
            print("\n⏭️ ALREADY APPLIED TO THIS JOB")
            print(f"   Reason: {result.get('reason', 'Duplicate application')}")
        elif status == "skipped":
            print("\n⏭️ APPLICATION SKIPPED")
            print(f"   Reason: {result.get('reason', 'Unknown')}")
        elif status == "error":
            print("\n❌ APPLICATION FAILED")
            print(f"   Error: {result.get('error', 'Unknown error')}")
        else:
            print(f"\n⚠️ UNEXPECTED STATUS: {status}")
            if result.get("reason"):
                print(f"   Reason: {result.get('reason')}")
            if result.get("error"):
                print(f"   Error: {result.get('error')}")
        
        print("\n" + "="*70 + "\n")
        
        # Check database to confirm
        try:
            from app.core.supabase_client import get_supabase
            supabase = get_supabase()
            db_result = supabase.table("applications").select("*").eq("user_id", USER_ID).eq("url", JOB_URL).execute()
            
            if db_result.data and len(db_result.data) > 0:
                print("✅ Application confirmed in database!")
                app = db_result.data[0]
                print(f"   Company: {app.get('company', 'N/A')}")
                print(f"   Role: {app.get('role', 'N/A')}")
                print(f"   Date: {app.get('date_applied', 'N/A')[:19]}")
                print()
        except Exception as e:
            print(f"⚠️ Could not verify in database: {e}\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Process interrupted by user")
    except Exception as e:
        print(f"\n\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

