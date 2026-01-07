"""
Simple Resume Service - Just use one resume file
No complex generation, no datasets, just effectiveness
"""

import os
from typing import Optional

# Default resume path - user should have one good resume
DEFAULT_RESUME_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "storage",
    "resumes",
    "pdf",
    "resume.pdf"
)


def get_resume_path(resume_path: Optional[str] = None) -> str:
    """
    Get the resume file path to use for applications.
    
    Args:
        resume_path: Optional custom resume path. If None, uses default.
    
    Returns:
        Path to resume PDF file
    """
    if resume_path and os.path.exists(resume_path):
        return resume_path
    
    # Use default resume
    if os.path.exists(DEFAULT_RESUME_PATH):
        return DEFAULT_RESUME_PATH
    
    # If default doesn't exist, check for any PDF in resumes folder
    resumes_dir = os.path.dirname(DEFAULT_RESUME_PATH)
    if os.path.exists(resumes_dir):
        for file in os.listdir(resumes_dir):
            if file.endswith('.pdf'):
                return os.path.join(resumes_dir, file)
    
    raise FileNotFoundError(
        f"Resume not found. Please place your resume PDF at: {DEFAULT_RESUME_PATH}"
    )


def get_cover_letter_path(cover_letter_path: Optional[str] = None) -> Optional[str]:
    """
    Get the cover letter file path (optional).
    
    Args:
        cover_letter_path: Optional custom cover letter path.
    
    Returns:
        Path to cover letter file, or None if not available
    """
    if cover_letter_path and os.path.exists(cover_letter_path):
        return cover_letter_path
    
    # Check for default cover letter
    default_cover_letter = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "storage",
        "cover_letters",
        "cover_letter.txt"
    )
    
    if os.path.exists(default_cover_letter):
        return default_cover_letter
    
    return None



