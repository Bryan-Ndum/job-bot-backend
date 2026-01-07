from fastapi import APIRouter
from pydantic import BaseModel

from app.services.resume_service import generate_resume

router = APIRouter()

class ResumeRequest(BaseModel):
    job_description: str
    user_id: str = "bryan"

@router.post("/generate")
def generate_resume_endpoint(payload: ResumeRequest):
    pdf_url, dataset_used, score = generate_resume(payload.job_description, payload.user_id)
    return {
        "resume_pdf_url": pdf_url,
        "dataset_used": dataset_used,
        "match_score": score
    }
