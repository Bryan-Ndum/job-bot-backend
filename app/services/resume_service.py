# This file appears to be unused/legacy code
# The actual resume generation is handled by:
# - app/services/resume_engine/generator.py
# - app/services/resume_optimizer.py
# - app/services/resume_pipeline.py

from app.services.resume_pipeline import generate_resume_pipeline

def generate_resume(job_description: str, user_id: str):
    """
    Legacy function - redirects to resume pipeline.
    """
    result = generate_resume_pipeline(job_description)
    
    # Return in expected format for compatibility
    return (
        result.get("pdf_url", ""),
        result.get("dataset_name", "general"),
        result.get("match_score", 0)
    )
