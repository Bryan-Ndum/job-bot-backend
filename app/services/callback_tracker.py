"""
Callback Tracking and Optimization Module
Tracks application results and optimizes for callback rate.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional
from app.core.supabase_client import get_supabase


def track_application(
    application_id: str,
    company: str,
    role: str,
    fit_score: float,
    resume_version: str,
    cover_letter_version: str,
    url: str,
    user_id: str,
    job_id: Optional[str] = None
) -> Dict:
    """
    Store application record for tracking.
    """
    try:
        supabase = get_supabase()
        record = {
            "application_id": application_id,
            "user_id": user_id,
            "company": company,
            "role": role,
            "fit_score": fit_score,
            "resume_version": resume_version,
            "cover_letter_version": cover_letter_version,
            "url": url,
            "date_applied": datetime.utcnow().isoformat(),
            "callback_status": "pending",
            "callback_date": None,
            "interview_date": None,
            "rejection_date": None,
            "notes": ""
        }
        
        # Add job_id if provided (for better duplicate detection)
        if job_id:
            record["job_id"] = job_id
        
        result = supabase.table("applications").insert(record).execute()
        print(f"   ✓ Application tracked in database: {application_id}")
        return {"status": "success", "data": result.data}
    except Exception as e:
        error_msg = str(e)
        # Check if it's a schema issue
        if "column" in error_msg.lower() and ("does not exist" in error_msg.lower() or "42703" in error_msg):
            print(f"   ⚠️ Database schema issue: {error_msg}")
            print(f"   Please run fix_database_schema.sql in Supabase SQL Editor")
        else:
            print(f"   ⚠️ Could not track application: {error_msg}")
        return {"status": "error", "error": error_msg}


def update_callback_status(
    application_id: str,
    status: str,
    callback_date: Optional[str] = None,
    interview_date: Optional[str] = None,
    notes: Optional[str] = None
) -> Dict:
    """
    Update callback status: pending, callback, interview, rejected, no_response
    """
    try:
        supabase = get_supabase()
        update_data = {
            "callback_status": status,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        if callback_date:
            update_data["callback_date"] = callback_date
        if interview_date:
            update_data["interview_date"] = interview_date
        if notes:
            update_data["notes"] = notes
            
        result = supabase.table("applications").update(update_data).eq("application_id", application_id).execute()
        return {"status": "success", "data": result.data}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def get_callback_statistics(user_id: str, days: int = 30) -> Dict:
    """
    Get callback statistics for optimization.
    """
    try:
        supabase = get_supabase()
        cutoff_date = datetime.utcnow().isoformat()
        
        # Get all applications in time period
        result = supabase.table("applications").select("*").eq("user_id", user_id).gte("date_applied", cutoff_date).execute()
        
        applications = result.data if result.data else []
        
        total = len(applications)
        callbacks = len([a for a in applications if a.get("callback_status") in ["callback", "interview"]])
        interviews = len([a for a in applications if a.get("callback_status") == "interview"])
        rejections = len([a for a in applications if a.get("callback_status") == "rejected"])
        pending = len([a for a in applications if a.get("callback_status") == "pending"])
        
        callback_rate = (callbacks / total * 100) if total > 0 else 0
        interview_rate = (interviews / total * 100) if total > 0 else 0
        
        # Analyze resume version performance
        resume_performance = {}
        for app in applications:
            resume_ver = app.get("resume_version", "unknown")
            if resume_ver not in resume_performance:
                resume_performance[resume_ver] = {"total": 0, "callbacks": 0, "interviews": 0}
            
            resume_performance[resume_ver]["total"] += 1
            if app.get("callback_status") in ["callback", "interview"]:
                resume_performance[resume_ver]["callbacks"] += 1
            if app.get("callback_status") == "interview":
                resume_performance[resume_ver]["interviews"] += 1
        
        # Calculate callback rates per resume version
        for ver, stats in resume_performance.items():
            stats["callback_rate"] = (stats["callbacks"] / stats["total"] * 100) if stats["total"] > 0 else 0
            stats["interview_rate"] = (stats["interviews"] / stats["total"] * 100) if stats["total"] > 0 else 0
        
        return {
            "total_applications": total,
            "callbacks": callbacks,
            "interviews": interviews,
            "rejections": rejections,
            "pending": pending,
            "callback_rate": round(callback_rate, 2),
            "interview_rate": round(interview_rate, 2),
            "resume_performance": resume_performance
        }
    except Exception as e:
        return {"error": str(e)}


def get_optimal_resume_version(user_id: str) -> str:
    """
    Determine which resume version performs best based on callback data.
    """
    stats = get_callback_statistics(user_id)
    
    if "resume_performance" not in stats or not stats["resume_performance"]:
        return "default"  # Fallback
    
    # Find resume version with highest callback rate
    best_version = max(
        stats["resume_performance"].items(),
        key=lambda x: x[1].get("callback_rate", 0)
    )
    
    return best_version[0]


def get_high_performing_elements(user_id: str) -> Dict:
    """
    Analyze which resume elements (summaries, skills order, bullets) generate callbacks.
    """
    try:
        supabase = get_supabase()
        # Get applications with callbacks
        result = supabase.table("applications").select("*").eq("user_id", user_id).in_("callback_status", ["callback", "interview"]).execute()
        
        callback_apps = result.data if result.data else []
        
        # Analyze patterns (this would be enhanced with more detailed resume metadata)
        high_fit_scores = [app.get("fit_score", 0) for app in callback_apps]
        avg_fit_score = sum(high_fit_scores) / len(high_fit_scores) if high_fit_scores else 0
        
        return {
            "avg_fit_score_for_callbacks": round(avg_fit_score, 2),
            "total_callbacks_analyzed": len(callback_apps),
            "recommendation": "Focus on jobs with fit_score >= 80 for best results"
        }
    except Exception as e:
        return {"error": str(e)}


def batch_update_callbacks(updates: List[Dict]) -> Dict:
    """
    Batch update multiple application callback statuses.
    """
    results = []
    for update in updates:
        app_id = update.get("application_id")
        status = update.get("callback_status")
        result = update_callback_status(app_id, status, update.get("callback_date"), update.get("interview_date"), update.get("notes"))
        results.append(result)
    
    return {"updated": len(results), "results": results}

