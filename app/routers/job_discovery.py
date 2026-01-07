"""
FastAPI Router for Job Discovery System
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import asyncio
from concurrent.futures import ThreadPoolExecutor
from app.services.job_discovery import discover_and_apply

router = APIRouter(prefix="/api/jobs", tags=["job-discovery"])


class JobDiscoveryRequest(BaseModel):
    keywords: str
    location: str = ""
    user_id: str
    user_info: Dict
    sources: List[str] = ["linkedin", "indeed"]
    limit_per_source: int = 25
    exclude_keywords: Optional[List[str]] = None
    include_keywords: Optional[List[str]] = None
    min_fit_score: int = 40
    auto_apply: bool = True


# Thread pool for running blocking operations  
# Use a dedicated executor for Playwright to avoid asyncio conflicts
executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="playwright")

def run_discover_and_apply_safely(**kwargs):
    """
    Run discover_and_apply in a clean thread context.
    Ensure nest_asyncio is applied and event loop context is cleared.
    """
    import asyncio
    import threading
    
    # Apply nest_asyncio in this thread
    try:
        import nest_asyncio
        nest_asyncio.apply()
    except (ImportError, Exception):
        pass
    
    # Try to clear any event loop reference in this thread
    try:
        thread = threading.current_thread()
        # Remove event loop references
        if hasattr(thread, '__dict__'):
            thread.__dict__.pop('_event_loop', None)
            thread.__dict__.pop('_asyncio_event_loop', None)
    except Exception:
        pass
    
    # Run the discovery function
    return discover_and_apply(**kwargs)


@router.post("/discover-and-apply")
async def discover_and_apply_endpoint(request: JobDiscoveryRequest):
    """
    Discover jobs from multiple job boards and apply automatically.
    
    Note: This is a long-running operation (30-60 minutes for 50 jobs).
    The browser will open automatically for job discovery and applications.
    
    ⚠️ WARNING: This will timeout on HTTP requests. For production, use
    background jobs (Celery) or Server-Sent Events for real-time updates.
    """
    import traceback
    
    try:
        # Run the blocking function in a thread pool to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        
        # Use functools.partial to pass all arguments to the safe wrapper
        from functools import partial
        discover_func = partial(
            run_discover_and_apply_safely,
            keywords=request.keywords,
            location=request.location,
            user_info=request.user_info,
            user_id=request.user_id,
            sources=request.sources,
            limit_per_source=request.limit_per_source,
            exclude_keywords=request.exclude_keywords,
            include_keywords=request.include_keywords,
            min_fit_score=request.min_fit_score,
            auto_apply=request.auto_apply
        )
        
        result = await loop.run_in_executor(executor, discover_func)
        
        return result
        
    except Exception as e:
        error_detail = str(e)
        error_traceback = traceback.format_exc()
        print(f"❌ Error in discover_and_apply_endpoint: {error_detail}")
        print(f"Traceback: {error_traceback}")
        raise HTTPException(
            status_code=500, 
            detail={
                "error": error_detail,
                "message": "Job discovery failed. Check server logs for details.",
                "traceback": error_traceback
            }
        )


@router.get("/discover/status")
async def get_discovery_status():
    """
    Get current discovery status (if running).
    TODO: Implement job status tracking
    """
    return {
        "status": "idle",
        "message": "Discovery status tracking not yet implemented"
    }

