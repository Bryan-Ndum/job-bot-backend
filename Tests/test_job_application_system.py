"""
Test script for the automated job application system.
Demonstrates the full pipeline from job intake to application.
"""

import sys
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(ROOT)
if PARENT not in sys.path:
    sys.path.insert(0, PARENT)

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from app.services.job_application_orchestrator import apply_to_job, apply_to_jobs_batch


def test_single_job():
    """Test processing a single job URL."""
    print("\n" + "="*60)
    print("🧪 TESTING SINGLE JOB APPLICATION")
    print("="*60 + "\n")
    
    # Example job URL and description
    url = "https://www.linkedin.com/jobs/view/1234567890"
    job_description = """
    IT Support Analyst
    
    We are looking for an IT Support Analyst to join our team. 
    The ideal candidate will have experience with:
    - Windows troubleshooting
    - Azure cloud services
    - Network fundamentals
    - IT support and helpdesk operations
    
    Requirements:
    - Bachelor's degree in IT, Cybersecurity, or related field
    - 1-2 years of IT support experience
    - Strong problem-solving skills
    """
    
    user_id = "test_user_123"
    user_info = {
        "first_name": "Bryan",
        "last_name": "Ndum",
        "email": "bryanndum12@gmail.com",
        "phone": "",
        "location": "Remote, NC",
        "linkedin": ""
    }
    
    # Process job (without auto-apply for testing)
    result = apply_to_job(
        url=url,
        job_description=job_description,
        user_id=user_id,
        user_info=user_info,
        auto_apply=False  # Set to True to actually apply
    )
    
    print("\n" + "="*60)
    print("📊 RESULTS")
    print("="*60)
    print(f"Job ID: {result.get('job_id')}")
    print(f"Company: {result.get('company')}")
    print(f"Role: {result.get('role')}")
    print(f"Fit Score: {result.get('fit_score')}")
    print(f"Decision: {result.get('decision')}")
    print(f"Reason: {result.get('reason')}")
    print(f"Status: {result.get('status')}")
    
    if result.get('resume_path'):
        print(f"Resume: {result.get('resume_path')}")
    if result.get('cover_letter_path'):
        print(f"Cover Letter: {result.get('cover_letter_path')}")
    
    print("="*60 + "\n")
    
    return result


def test_batch_jobs():
    """Test processing multiple jobs in batch."""
    print("\n" + "="*60)
    print("🧪 TESTING BATCH JOB APPLICATION")
    print("="*60 + "\n")
    
    job_inputs = [
        {
            "url": "https://www.linkedin.com/jobs/view/1111111111",
            "description": "Cybersecurity Analyst role requiring Python, Linux, and security tools."
        },
        {
            "url": "https://www.linkedin.com/jobs/view/2222222222",
            "description": "IT Support position with Windows, Azure, and networking experience."
        },
        {
            "url": "https://www.linkedin.com/jobs/view/3333333333",
            "description": "Senior Software Engineer - requires 10+ years experience with Java."
        }
    ]
    
    user_id = "test_user_123"
    user_info = {
        "first_name": "Bryan",
        "last_name": "Ndum",
        "email": "bryanndum12@gmail.com"
    }
    
    # Process batch (without auto-apply)
    result = apply_to_jobs_batch(
        job_inputs=job_inputs,
        user_id=user_id,
        user_info=user_info,
        auto_apply=False,
        min_score=65
    )
    
    print("\n" + "="*60)
    print("📊 BATCH RESULTS SUMMARY")
    print("="*60)
    print(f"Total Jobs: {result.get('total_jobs')}")
    print(f"Eligible Jobs: {result.get('eligible_jobs')}")
    print(f"Applied: {result.get('applied')}")
    print(f"Skipped: {result.get('skipped')}")
    print(f"Errors: {result.get('errors')}")
    print("="*60 + "\n")
    
    return result


if __name__ == "__main__":
    print("\n🚀 JOB APPLICATION SYSTEM TEST\n")
    
    # Test single job
    test_single_job()
    
    # Test batch processing
    # test_batch_jobs()  # Uncomment to test batch processing
    
    print("✅ Testing complete!\n")






