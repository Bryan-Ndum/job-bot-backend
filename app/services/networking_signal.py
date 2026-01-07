"""
Networking Signal Generation Module
Generates LinkedIn follow-up messages for applications.
"""

import re
from typing import Dict, Optional, List
from openai import OpenAI
from app.core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def generate_follow_up_message(
    company: str,
    role: str,
    job_description: str,
    recruiter_name: Optional[str] = None,
    company_info: Optional[str] = None
) -> Dict:
    """
    Generate a personalized LinkedIn follow-up message.
    
    Template structure:
    Hi [Name], I applied for the [Role] today. My experience with [X] aligns 
    closely with your team's work on [Y]. I'd love to connect and learn more.
    """
    
    # Extract key experience points from job description
    prompt = f"""
    Generate a short, professional LinkedIn follow-up message for a job application.
    
    Company: {company}
    Role: {role}
    Job Description: {job_description}
    Recruiter Name: {recruiter_name or "Hiring Manager"}
    Company Info: {company_info or "Not provided"}
    
    Requirements:
    - Start with "Hi [Name]," (use recruiter name if provided, otherwise "Hi,")
    - Mention that you applied for the role today
    - Reference 1-2 specific skills/experiences that align with the job
    - Reference something specific about the company/team if possible
    - Keep it under 100 words
    - Professional but warm tone
    - End with invitation to connect/learn more
    
    Return ONLY the message text, no extra formatting.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional networking expert. Write concise, personalized LinkedIn messages."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )
        
        message = response.choices[0].message.content.strip()
        
        return {
            "message": message,
            "recruiter_name": recruiter_name,
            "company": company,
            "role": role,
            "ready_to_send": True
        }
    except Exception as e:
        # Fallback template
        name = recruiter_name if recruiter_name else "there"
        fallback = f"""Hi {name},

I applied for the {role} position at {company} today. My experience with cybersecurity, IT support, and automation aligns closely with the role requirements. I'd love to connect and learn more about the team and opportunity.

Best regards,
Bryan Ndum"""
        
        return {
            "message": fallback,
            "recruiter_name": recruiter_name,
            "company": company,
            "role": role,
            "ready_to_send": True,
            "error": str(e)
        }


def find_recruiter_info(company: str, role: str) -> Dict:
    """
    Attempt to identify recruiter or hiring manager from LinkedIn.
    This would integrate with LinkedIn API or scraping (to be implemented).
    """
    # Placeholder - would use LinkedIn API or web scraping
    return {
        "recruiter_name": None,
        "recruiter_linkedin": None,
        "hiring_manager": None,
        "found": False
    }


def store_networking_contact(
    application_id: str,
    company: str,
    role: str,
    recruiter_name: Optional[str],
    recruiter_linkedin: Optional[str],
    message: str,
    user_id: str
) -> Dict:
    """
    Store networking contact information for follow-up tracking.
    """
    from datetime import datetime
    from app.core.supabase_client import get_supabase
    
    supabase = get_supabase()
    
    try:
        record = {
            "application_id": application_id,
            "user_id": user_id,
            "company": company,
            "role": role,
            "recruiter_name": recruiter_name,
            "recruiter_linkedin": recruiter_linkedin,
            "message": message,
            "message_sent": False,
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table("networking_contacts").insert(record).execute()
        return {"status": "success", "data": result.data}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def generate_batch_follow_ups(applications: List[Dict]) -> List[Dict]:
    """
    Generate follow-up messages for multiple applications.
    """
    messages = []
    for app in applications:
        company = app.get("company", "")
        role = app.get("role", "")
        job_description = app.get("raw_description", "")
        
        recruiter_info = find_recruiter_info(company, role)
        
        message_data = generate_follow_up_message(
            company=company,
            role=role,
            job_description=job_description,
            recruiter_name=recruiter_info.get("recruiter_name"),
            company_info=None
        )
        
        message_data["application_id"] = app.get("application_id", "")
        messages.append(message_data)
    
    return messages

