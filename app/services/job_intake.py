"""
Job Intake and Parsing Module
Extracts structured data from job URLs, descriptions, and saved job lists.
"""

import re
import json
from typing import Dict, List, Optional
from urllib.parse import urlparse
from openai import OpenAI
from app.core.config import settings
from app.services.ats_detector import detect_ats

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def parse_job_from_url(url: str, job_description: Optional[str] = None) -> Dict:
    """
    Parse job information from URL and optional description.
    Extracts company, role, ATS type, skills, location, etc.
    """
    ats_type = detect_ats(url)
    
    # If description not provided, try to extract from URL/page
    if not job_description:
        job_description = f"Job posting at {url}"
    
    # Use AI to extract structured information
    extraction_prompt = f"""
Extract structured information from this job posting:

URL: {url}
Job Description:
{job_description}

Return ONLY valid JSON with these exact keys:
{{
  "company": "company name or empty string",
  "role": "job title/role name",
  "ats_type": "{ats_type}",
  "required_skills": ["skill1", "skill2", ...],
  "preferred_skills": ["skill1", "skill2", ...],
  "tech_stack": ["technology1", "technology2", ...],
  "seniority": "entry-level|mid-level|senior|lead|other",
  "location": "city, state or 'remote' or 'hybrid'",
  "keywords": ["keyword1", "keyword2", ...]
}}

Focus on:
- Required skills: must-have qualifications
- Preferred skills: nice-to-have qualifications  
- Tech stack: specific technologies/frameworks/tools
- Seniority: level based on years/experience requirements
- Location: extract if mentioned, otherwise "remote" if remote-friendly
- Keywords: important terms for matching

Return ONLY the JSON object, no extra text.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a job parsing expert. Extract structured data and return ONLY valid JSON."},
                {"role": "user", "content": extraction_prompt}
            ],
            temperature=0.1
        )
        
        content = response.choices[0].message.content.strip()
        
        # Clean up JSON if wrapped in markdown code blocks
        if content.startswith("```"):
            content = re.sub(r'^```json\n?', '', content)
            content = re.sub(r'```\n?$', '', content)
        
        job_data = json.loads(content)
        
        # Generate job_id from URL or company+role
        job_id = generate_job_id(url, job_data.get("company", ""), job_data.get("role", ""))
        
        return {
            "job_id": job_id,
            "company": job_data.get("company", ""),
            "role": job_data.get("role", ""),
            "ats_type": job_data.get("ats_type", ats_type),
            "required_skills": job_data.get("required_skills", []),
            "preferred_skills": job_data.get("preferred_skills", []),
            "tech_stack": job_data.get("tech_stack", []),
            "seniority": job_data.get("seniority", "other"),
            "location": job_data.get("location", ""),
            "keywords": job_data.get("keywords", []),
            "url": url,
            "raw_description": job_description
        }
        
    except Exception as e:
        # Fallback parsing
        return {
            "job_id": generate_job_id(url, "", ""),
            "company": extract_company_from_url(url),
            "role": extract_role_from_url(url),
            "ats_type": ats_type,
            "required_skills": [],
            "preferred_skills": [],
            "tech_stack": [],
            "seniority": "other",
            "location": "",
            "keywords": [],
            "url": url,
            "raw_description": job_description
        }


def parse_job_from_description(job_description: str, url: Optional[str] = None) -> Dict:
    """
    Parse job information from text description.
    """
    if url:
        return parse_job_from_url(url, job_description)
    
    # Extract without URL
    return parse_job_from_url("unknown", job_description)


def parse_job_batch(job_inputs: List[Dict]) -> List[Dict]:
    """
    Parse multiple jobs from batch input.
    Input format: [{"url": "...", "description": "..."}, ...]
    """
    results = []
    for job_input in job_inputs:
        url = job_input.get("url", "")
        description = job_input.get("description", "")
        
        if url:
            parsed = parse_job_from_url(url, description)
        else:
            parsed = parse_job_from_description(description)
        
        results.append(parsed)
    
    return results


def generate_job_id(url: str, company: str, role: str) -> str:
    """Generate a unique job ID from URL, company, and role."""
    import hashlib
    
    # Use URL as primary source, fallback to company+role
    identifier = url if url and url != "unknown" else f"{company}_{role}"
    return hashlib.md5(identifier.encode()).hexdigest()[:16]


def extract_company_from_url(url: str) -> str:
    """Extract company name from URL as fallback."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        # Remove www., jobs., careers., etc.
        domain = re.sub(r'^(www\.|jobs\.|careers\.)', '', domain)
        # Extract company from domain (e.g., greenhouse.io/company-name -> company-name)
        return domain.split('.')[0] if domain else ""
    except:
        return ""


def extract_role_from_url(url: str) -> str:
    """Extract role from URL path as fallback."""
    try:
        parsed = urlparse(url)
        path_parts = [p for p in parsed.path.split('/') if p]
        # Usually role is in last part of path
        return path_parts[-1].replace('-', ' ').title() if path_parts else ""
    except:
        return ""

