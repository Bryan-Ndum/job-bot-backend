"""
FastAPI Router for Job Application System
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from app.services.job_application_orchestrator import apply_to_job, apply_to_jobs_batch

router = APIRouter(prefix="/api/jobs", tags=["job-application"])


class JobApplicationRequest(BaseModel):
    url: str
    job_description: Optional[str] = None
    user_id: str
    user_info: Optional[Dict] = None
    auto_apply: bool = False


class BatchJobApplicationRequest(BaseModel):
    jobs: List[Dict]  # [{"url": "...", "description": "..."}, ...]
    user_id: str
    user_info: Optional[Dict] = None
    auto_apply: bool = False
    min_score: int = 65


@router.post("/apply")
async def apply_to_single_job(request: JobApplicationRequest):
    """
    Apply to a single job URL.
    """
    try:
        result = apply_to_job(
            url=request.url,
            job_description=request.job_description,
            user_id=request.user_id,
            user_info=request.user_info,
            auto_apply=request.auto_apply
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/apply/batch")
async def apply_to_multiple_jobs(request: BatchJobApplicationRequest):
    """
    Apply to multiple jobs in batch.
    """
    try:
        result = apply_to_jobs_batch(
            job_inputs=request.jobs,
            user_id=request.user_id,
            user_info=request.user_info,
            auto_apply=request.auto_apply,
            min_score=request.min_score
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "system": "job-application-orchestrator"}






