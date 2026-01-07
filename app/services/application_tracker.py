"""
Application Tracker - Prevent duplicate applications
"""

import os
from typing import Dict, Optional
from app.core.supabase_client import get_supabase


def has_applied_to_url(url: str, user_id: str) -> bool:
    """
    Check if user has already applied to this job URL.
    
    Args:
        url: Job application URL
        user_id: User identifier
    
    Returns:
        True if already applied, False otherwise
    """
    try:
        supabase = get_supabase()
        
        # Check if application exists with this URL
        result = supabase.table("applications").select("id").eq("user_id", user_id).eq("url", url).limit(1).execute()
        
        if result.data and len(result.data) > 0:
            return True
        
        return False
    except Exception as e:
        # If database check fails, return False (allow application)
        # This prevents blocking applications if database is unavailable
        print(f"   ⚠️ Could not check duplicate: {e}")
        return False


def has_applied_to_job(job_id: str, user_id: str) -> bool:
    """
    Check if user has already applied to this job (by job_id).
    
    Args:
        job_id: Job identifier
        user_id: User identifier
    
    Returns:
        True if already applied, False otherwise
    """
    try:
        supabase = get_supabase()
        
        # Check if application exists with this job_id
        # Note: This requires job_id to be stored, which may not always be available
        result = supabase.table("applications").select("id").eq("user_id", user_id).eq("job_id", job_id).limit(1).execute()
        
        if result.data and len(result.data) > 0:
            return True
        
        return False
    except Exception as e:
        print(f"   ⚠️ Could not check duplicate: {e}")
        return False


def mark_url_as_applied(url: str, user_id: str, company: str = "", role: str = ""):
    """
    Mark a URL as applied (for session-based tracking without database).
    This is a simple in-memory cache for the current session.
    """
    # This could be expanded to use a file-based cache or database
    # For now, this is just a placeholder - the real tracking happens in callback_tracker
    pass


