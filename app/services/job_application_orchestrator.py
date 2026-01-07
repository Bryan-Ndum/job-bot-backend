"""
Main Job Application Orchestrator
Coordinates all components for high-volume automated job applications.
"""

import uuid
import time
from typing import Dict, List, Optional
from app.services.job_intake import parse_job_from_url, parse_job_batch
from app.services.job_fit_scorer import score_job_fit, filter_jobs_by_score
from app.services.resume_optimizer import generate_optimized_resume, generate_optimized_cover_letter
from app.services.playwright_apply import apply_with_playwright
import os
from app.services.callback_tracker import track_application
from app.services.networking_signal import generate_follow_up_message, store_networking_contact
from app.services.application_tracker import has_applied_to_url


class JobApplicationOrchestrator:
    """
    Main orchestrator for automated job application system.
    Optimized for callback rate, not just application volume.
    """
    
    def __init__(self, user_id: str, user_info: Optional[Dict] = None):
        self.user_id = user_id
        self.user_info = user_info or {
            "first_name": "Bryan",
            "last_name": "Ndum",
            "email": "bryanndum12@gmail.com",
            "phone": "984-274-7193",
            "location": "Clayton, North Carolina",
            "linkedin": "https://www.linkedin.com/in/bryan-ndum-99488b23a/"
        }
    
    def process_job_url(
        self,
        url: str,
        job_description: Optional[str] = None,
        auto_apply: bool = False,
        min_fit_score: int = 65
    ) -> Dict:
        """
        Process a single job URL through the full pipeline.
        
        Steps:
        1. Parse job data
        2. Score job fit
        3. If score >= min_fit_score: generate optimized resume/cover letter
        4. If auto_apply and score >= min_fit_score: apply automatically
        5. Track application
        6. Generate networking signal
        
        Args:
            url: Job application URL
            job_description: Optional pre-fetched job description
            auto_apply: Whether to automatically submit application
            min_fit_score: Minimum fit score threshold (0-100). Jobs below this are skipped.
        """
        
        result = {
            "job_id": None,
            "fit_score": 0,
            "decision": "skip",
            "application_id": None,
            "status": "pending",
            "duration_seconds": 0
        }
        
        start_time = time.time()
        
        try:
            # Step 0: Check if already applied (prevent duplicates)
            if has_applied_to_url(url, self.user_id):
                result["status"] = "duplicate"
                result["reason"] = "Already applied to this job"
                print(f"⏭️ Skipping duplicate: Already applied to this job URL")
                return result
            
            # Step 1: Parse job
            print(f"📥 Parsing job from URL: {url}")
            job_data = parse_job_from_url(url, job_description)
            result["job_id"] = job_data.get("job_id")
            result["company"] = job_data.get("company")
            result["role"] = job_data.get("role")
            
            # Step 2: Score job fit
            print(f"📊 Scoring job fit...")
            scored_job = score_job_fit(job_data)
            result["fit_score"] = scored_job.get("fit_score", 0)
            result["decision"] = scored_job.get("decision", "skip")
            result["reason"] = scored_job.get("reason", "")
            
            # Step 3: Decision logic - respect min_fit_score threshold
            # Override decision if fit score meets threshold (even if scorer says skip)
            if result["fit_score"] >= min_fit_score:
                result["decision"] = "apply"
                print(f"✅ Job meets threshold (fit score: {result['fit_score']:.1f} >= {min_fit_score})")
            elif result["decision"] == "skip":
                print(f"⏭️ Skipping job (fit score: {result['fit_score']:.1f} < {min_fit_score})")
                result["status"] = "skipped"
                result["reason"] = f"Fit score {result['fit_score']:.1f} below threshold {min_fit_score}"
                return result
            
            # Step 4: Get resume and cover letter paths (simplified - use existing files)
            print(f"📄 Getting resume and cover letter...")
            from app.services.simple_resume_service import get_resume_path, get_cover_letter_path
            
            resume_path = get_resume_path()
            cover_letter_path = get_cover_letter_path()
            
            resume_data = {
                "pdf_resume": resume_path,
                "resume_version": "default"
            }
            cover_letter_data = {
                "cover_letter": cover_letter_path
            }
            
            # Step 5: Auto-apply if requested
            if auto_apply:
                print(f"🤖 Starting automated application...")
                application_id = str(uuid.uuid4())
                
                # Use async Playwright wrapper to avoid sync API conflicts
                from app.services.playwright_apply_async_wrapper import apply_with_playwright_async_wrapper
                apply_result = apply_with_playwright_async_wrapper(
                    url=url,
                    resume_path=resume_data["pdf_resume"],
                    cover_letter_path=cover_letter_data.get("cover_letter"),
                    user_info=self.user_info,
                    headless=False,
                    captcha_service="2captcha",
                    captcha_api_key=os.getenv("CAPTCHA_2CAPTCHA_API_KEY")
                )
                
                result["application_id"] = application_id
                result["apply_result"] = apply_result
                
                # Step 6: Track application
                tracking_result = track_application(
                    application_id=application_id,
                    company=job_data.get("company", ""),
                    role=job_data.get("role", ""),
                    fit_score=result["fit_score"],
                    resume_version=resume_data.get("resume_version", "default"),
                    cover_letter_version=cover_letter_data.get("customization_level", "default"),
                    url=url,
                    user_id=self.user_id,
                    job_id=result.get("job_id")
                )
                
                # Log tracking status (but don't fail the application if tracking fails)
                if tracking_result.get("status") == "error":
                    print(f"   ⚠️ Warning: Application submitted but tracking failed")
                    result["tracking_error"] = tracking_result.get("error", "Unknown error")
                
                # Step 7: Generate networking signal
                print(f"📧 Generating networking follow-up message...")
                networking_message = generate_follow_up_message(
                    company=job_data.get("company", ""),
                    role=job_data.get("role", ""),
                    job_description=job_data.get("raw_description", "")
                )
                
                store_networking_contact(
                    application_id=application_id,
                    company=job_data.get("company", ""),
                    role=job_data.get("role", ""),
                    recruiter_name=networking_message.get("recruiter_name"),
                    recruiter_linkedin=None,
                    message=networking_message.get("message", ""),
                    user_id=self.user_id
                )
                
                result["networking_message"] = networking_message
                result["status"] = "applied"
            else:
                result["status"] = "ready_to_apply"
                result["resume_path"] = resume_data["pdf_resume"]
                result["cover_letter_path"] = cover_letter_data.get("cover_letter")
            
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            print(f"❌ Error processing job: {e}")
        
        # Calculate and add duration
        duration = time.time() - start_time
        result["duration_seconds"] = round(duration, 2)
        
        # Format duration for display
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        if minutes > 0:
            result["duration"] = f"{minutes}m {seconds}s"
        else:
            result["duration"] = f"{seconds}s"
        
        return result
    
    def process_job_batch(
        self,
        job_inputs: List[Dict],
        auto_apply: bool = False,
        min_score: int = 65
    ) -> Dict:
        """
        Process multiple jobs in batch.
        
        Input format: [{"url": "...", "description": "..."}, ...]
        """
        
        print(f"📦 Processing batch of {len(job_inputs)} jobs...")
        
        # Step 1: Parse all jobs
        parsed_jobs = parse_job_batch(job_inputs)
        
        # Step 2: Score all jobs
        scored_jobs = []
        for job in parsed_jobs:
            scored = score_job_fit(job)
            scored_jobs.append(scored)
        
        # Step 3: Filter by minimum score
        eligible_jobs = filter_jobs_by_score(scored_jobs, min_score=min_score)
        
        print(f"✅ {len(eligible_jobs)} jobs meet minimum score threshold ({min_score})")
        
        # Step 4: Process eligible jobs
        results = []
        for scored_job in eligible_jobs:
            job_data = scored_job.get("job_data", {})
            url = job_data.get("url", "")
            description = job_data.get("raw_description", "")
            
            result = self.process_job_url(
                url=url,
                job_description=description,
                auto_apply=auto_apply
            )
            results.append(result)
        
        # Summary
        summary = {
            "total_jobs": len(job_inputs),
            "eligible_jobs": len(eligible_jobs),
            "applied": len([r for r in results if r.get("status") == "applied"]),
            "skipped": len([r for r in results if r.get("status") == "skipped"]),
            "errors": len([r for r in results if r.get("status") == "error"]),
            "results": results
        }
        
        return summary
    
    def process_saved_job_list(
        self,
        job_list_id: str,
        auto_apply: bool = False
    ) -> Dict:
        """
        Process a saved job list from database.
        """
        # This would fetch from Supabase
        # For now, placeholder
        return {"status": "not_implemented", "message": "Saved job list processing coming soon"}


def apply_to_job(
    url: str,
    job_description: Optional[str] = None,
    user_id: str = "default",
    user_info: Optional[Dict] = None,
    auto_apply: bool = False
) -> Dict:
    """
    Convenience function to apply to a single job.
    """
    orchestrator = JobApplicationOrchestrator(user_id, user_info)
    return orchestrator.process_job_url(url, job_description, auto_apply)


def apply_to_jobs_batch(
    job_inputs: List[Dict],
    user_id: str = "default",
    user_info: Optional[Dict] = None,
    auto_apply: bool = False,
    min_score: int = 65
) -> Dict:
    """
    Convenience function to apply to multiple jobs.
    """
    orchestrator = JobApplicationOrchestrator(user_id, user_info)
    return orchestrator.process_job_batch(job_inputs, auto_apply, min_score)

