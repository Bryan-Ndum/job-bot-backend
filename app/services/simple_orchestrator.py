"""
Simple Job Application Orchestrator
Focused on effectiveness: discover, filter, score, apply
No complex resume generation, no networking signals - just results
"""

import time
from typing import Dict, Optional
from app.services.job_intake import parse_job_from_url
from app.services.job_fit_scorer import score_job_fit
from app.services.simple_resume_service import get_resume_path, get_cover_letter_path
from app.services.playwright_apply_async_wrapper import apply_with_playwright_async_wrapper
import os


def apply_to_job_simple(
    url: str,
    job_description: Optional[str] = None,
    user_info: Dict = None,
    resume_path: Optional[str] = None,
    cover_letter_path: Optional[str] = None,
    min_fit_score: int = 40,
    auto_apply: bool = True
) -> Dict:
    """
    Simple job application - just the essentials.
    
    Steps:
    1. Parse job (get company, role, skills)
    2. Score fit (0-100)
    3. If score >= min_fit_score and auto_apply: Apply with Playwright
    4. Return result
    
    Args:
        url: Job application URL
        job_description: Optional pre-fetched description
        user_info: Your info (name, email, phone, etc.)
        resume_path: Path to your resume PDF (uses default if not provided)
        cover_letter_path: Path to cover letter (optional)
        min_fit_score: Minimum score to apply (default 40)
        auto_apply: Whether to actually submit (default True)
    
    Returns:
        Dict with status, fit_score, and details
    """
    
    start_time = time.time()
    
    result = {
        "url": url,
        "fit_score": 0,
        "status": "pending",
        "error": None,
        "duration_seconds": 0
    }
    
    # Default user info
    if not user_info:
        user_info = {
            "first_name": "Bryan",
            "last_name": "Ndum",
            "email": "bryanndum12@gmail.com",
            "phone": "984-274-7193",
            "location": "Clayton, North Carolina",
            "linkedin": "https://www.linkedin.com/in/bryan-ndum-99488b23a/"
        }
    
    try:
        # Step 1: Parse job
        print(f"📥 Parsing job: {url}")
        job_data = parse_job_from_url(url, job_description)
        result["company"] = job_data.get("company", "Unknown")
        result["role"] = job_data.get("role", "Unknown")
        
        # Step 2: Score fit
        print(f"📊 Scoring job fit...")
        scored = score_job_fit(job_data)
        result["fit_score"] = scored.get("fit_score", 0)
        result["decision"] = scored.get("decision", "skip")
        result["reason"] = scored.get("reason", "")
        
        # Step 3: Check if we should apply
        if result["fit_score"] < min_fit_score:
            result["status"] = "skipped"
            result["reason"] = f"Fit score {result['fit_score']:.1f} below threshold {min_fit_score}"
            print(f"⏭️ Skipped: {result['reason']}")
            return result
        
        # Step 4: Apply if requested
        if auto_apply:
            print(f"🤖 Applying to job (fit score: {result['fit_score']:.1f})...")
            
            # Get resume and cover letter paths
            resume = get_resume_path(resume_path)
            cover_letter = get_cover_letter_path(cover_letter_path)
            
            # Apply via Playwright
            apply_result = apply_with_playwright_async_wrapper(
                url=url,
                resume_path=resume,
                cover_letter_path=cover_letter,
                user_info=user_info,
                headless=False,
                captcha_service="2captcha",
                captcha_api_key=os.getenv("CAPTCHA_2CAPTCHA_API_KEY")
            )
            
            if apply_result.get("status") == "applied":
                result["status"] = "applied"
                print(f"✅ Successfully applied!")
            else:
                result["status"] = "error"
                result["error"] = apply_result.get("error", "Application failed")
                print(f"❌ Application failed: {result['error']}")
        else:
            result["status"] = "ready_to_apply"
            result["resume_path"] = get_resume_path(resume_path)
            print(f"✅ Ready to apply (score: {result['fit_score']:.1f})")
        
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        print(f"❌ Error: {e}")
    
    # Calculate duration
    result["duration_seconds"] = round(time.time() - start_time, 2)
    return result



