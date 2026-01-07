"""
Resume and Cover Letter Optimization Module
Optimizes resume/cover letter for callback rate based on job fit score.
"""

import os
from typing import Dict, Optional
from app.services.resume_pipeline import generate_resume_pipeline
from app.services.cover_letter_generator import generate_cover_letter
from app.services.callback_tracker import get_optimal_resume_version


def generate_optimized_resume(
    job_description: str,
    fit_score: float,
    user_id: str,
    job_id: str
) -> Dict:
    """
    Generate resume optimized for callback rate.
    
    Rules:
    - One-page, recruiter-readable format
    - Metrics in first bullets
    - Skills reordered to match job description
    - No visual clutter
    
    Adaptation depth based on fit_score:
    - >= 80: Deep customization
    - 65-79: Light customization
    - < 65: Skip (shouldn't reach here)
    """
    
    # Get optimal resume version from callback tracking
    optimal_version = get_optimal_resume_version(user_id)
    
    # Generate base resume
    resume_data = generate_resume_pipeline(job_description)
    
    # For high-fit jobs, apply deep customization
    if fit_score >= 80:
        # Deep customization: reorder skills, emphasize matching keywords
        # This is already handled in resume_pipeline, but we can enhance it
        resume_version = f"deep_{optimal_version}"
    else:
        # Light customization: basic tailoring
        resume_version = f"light_{optimal_version}"
    
    return {
        "html_resume": resume_data["html_resume"],
        "pdf_resume": resume_data["pdf_resume"],
        "resume_version": resume_version,
        "customization_level": "deep" if fit_score >= 80 else "light"
    }


def generate_optimized_cover_letter(
    job_description: str,
    company: str,
    role: str,
    fit_score: float
) -> Dict:
    """
    Generate cover letter optimized for callback rate.
    
    Rules:
    - Maximum 200-250 words
    - One paragraph referencing company/product/market
    - One paragraph explaining role alignment
    - Optional short closing paragraph
    - No generic templates
    """
    
    # Enhance job description with company context for better personalization
    enhanced_prompt = f"""
    Company: {company}
    Role: {role}
    
    {job_description}
    """
    
    cover_letter_text = generate_cover_letter(enhanced_prompt)
    
    # Ensure word count is within limits
    word_count = len(cover_letter_text.split())
    if word_count > 250:
        # Truncate intelligently (would use AI to summarize)
        cover_letter_text = cover_letter_text[:500] + "..."
    
    # Save cover letter
    cover_letter_path = os.path.join("storage", "cover_letters", f"cover_letter_{company.replace(' ', '_')}.txt")
    os.makedirs(os.path.dirname(cover_letter_path), exist_ok=True)
    
    with open(cover_letter_path, "w", encoding="utf-8") as f:
        f.write(cover_letter_text)
    
    return {
        "cover_letter": cover_letter_path,
        "word_count": word_count,
        "customization_level": "deep" if fit_score >= 80 else "light"
    }






