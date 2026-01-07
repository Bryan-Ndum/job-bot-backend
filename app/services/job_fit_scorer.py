"""
Job Fit Probability Scoring Module
Scores jobs 0-100 based on callback likelihood.
"""

import json
from typing import Dict, List
from openai import OpenAI
from app.core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

# Candidate profile (should be loaded from config/database)
CANDIDATE_PROFILE = {
    "skills": [
        "Python", "Cybersecurity", "Cloud Security", "Linux", "Networking",
        "Azure", "AWS", "Machine Learning", "Data Analytics", "IT Support",
        "Troubleshooting", "Documentation", "Automation", "Scripting"
    ],
    "tech_stack": [
        "Python", "Linux", "Azure", "AWS", "Docker", "Git", "SQL",
        "PowerShell", "Bash", "Jenkins", "CI/CD"
    ],
    "seniority": "mid-level",  # Based on experience
    "locations_preferred": ["Remote", "NC", "US"],
    "visa_status": "authorized"  # US work authorization
}


def score_job_fit(job_data: Dict) -> Dict:
    """
    Score a job from 0-100 based on callback likelihood.
    
    Scoring factors:
    - Required skill overlap (high weight)
    - Tool and tech stack match (high weight)
    - Resume keyword alignment (medium)
    - Seniority alignment (medium)
    - Industry familiarity (medium)
    - Location and visa compatibility (medium)
    """
    
    # Extract job details
    required_skills = [s.lower() for s in job_data.get("required_skills", [])]
    preferred_skills = [s.lower() for s in job_data.get("preferred_skills", [])]
    tech_stack = [t.lower() for t in job_data.get("tech_stack", [])]
    seniority = job_data.get("seniority", "other").lower()
    location = job_data.get("location", "").lower()
    keywords = [k.lower() for k in job_data.get("keywords", [])]
    
    candidate_skills = [s.lower() for s in CANDIDATE_PROFILE["skills"]]
    candidate_tech = [t.lower() for t in CANDIDATE_PROFILE["tech_stack"]]
    
    scores = {}
    
    # 1. Required skill overlap (30 points)
    if required_skills:
        overlap = len(set(required_skills) & set(candidate_skills))
        skill_score = min(30, (overlap / len(required_skills)) * 30)
    else:
        skill_score = 15  # Neutral if no required skills listed
    scores["required_skills"] = skill_score
    
    # 2. Tech stack match (25 points)
    if tech_stack:
        tech_overlap = len(set(tech_stack) & set(candidate_tech))
        tech_score = min(25, (tech_overlap / len(tech_stack)) * 25)
    else:
        tech_score = 12.5
    scores["tech_stack"] = tech_score
    
    # 3. Preferred skills bonus (10 points)
    if preferred_skills:
        pref_overlap = len(set(preferred_skills) & set(candidate_skills))
        pref_score = min(10, (pref_overlap / len(preferred_skills)) * 10)
    else:
        pref_score = 5
    scores["preferred_skills"] = pref_score
    
    # 4. Seniority alignment (10 points)
    candidate_seniority = CANDIDATE_PROFILE["seniority"].lower()
    seniority_matches = {
        ("entry-level", "entry-level"): 10,
        ("mid-level", "mid-level"): 10,
        ("senior", "senior"): 10,
        ("lead", "lead"): 10,
        ("entry-level", "mid-level"): 7,  # Can apply up
        ("mid-level", "senior"): 7,
        ("senior", "lead"): 8,
        ("mid-level", "entry-level"): 3,  # Overqualified
        ("senior", "mid-level"): 3,
        ("lead", "senior"): 3,
    }
    seniority_key = (candidate_seniority, seniority)
    seniority_score = seniority_matches.get(seniority_key, 5)
    scores["seniority"] = seniority_score
    
    # 5. Location compatibility (10 points)
    location_score = 5  # Default neutral
    if "remote" in location:
        location_score = 10
    elif any(loc in location for loc in CANDIDATE_PROFILE["locations_preferred"]):
        location_score = 8
    scores["location"] = location_score
    
    # 6. Keyword alignment (10 points)
    all_candidate_keywords = candidate_skills + candidate_tech
    keyword_overlap = len(set(keywords) & set(all_candidate_keywords))
    if keywords:
        keyword_score = min(10, (keyword_overlap / len(keywords)) * 10)
    else:
        keyword_score = 5
    scores["keywords"] = keyword_score
    
    # 7. Industry/domain familiarity (5 points) - bonus for relevant domains
    domain_bonus = 5  # Default
    if any(kw in ["cybersecurity", "security", "cyber"] for kw in keywords):
        domain_bonus = 5
    elif any(kw in ["it", "support", "troubleshooting"] for kw in keywords):
        domain_bonus = 5
    scores["domain_familiarity"] = domain_bonus
    
    # Check for security clearance requirements - auto-reject
    clearance_keywords = [
        "security clearance", "secret clearance", "top secret", "ts/sci", "ts/sci clearance",
        "active clearance", "dod clearance", "government clearance", "clearance required",
        "must have clearance", "clearance eligibility", "eligible for clearance"
    ]
    description_text = job_data.get("raw_description", "").lower()
    if any(keyword in description_text for keyword in clearance_keywords):
        total_score = 0
        decision = "skip"
        reason = "Requires security clearance - not eligible"
    else:
        # Calculate total score
        total_score = sum(scores.values())
        total_score = min(100, max(0, total_score))  # Clamp to 0-100
        
        # Determine decision
        if total_score >= 80:
            decision = "apply"
            reason = "High fit score - strong skill and tech stack alignment"
        elif total_score >= 65:
            decision = "apply"
            reason = "Good fit - solid alignment with some gaps"
        else:
            decision = "skip"
            reason = f"Low fit score ({total_score:.1f}) - insufficient alignment"
    
    return {
        "job_id": job_data.get("job_id", ""),
        "fit_score": round(total_score, 1),
        "decision": decision,
        "reason": reason,
        "score_breakdown": scores,
        "job_data": job_data
    }


def batch_score_jobs(job_list: List[Dict]) -> List[Dict]:
    """Score multiple jobs."""
    results = []
    for job in job_list:
        scored = score_job_fit(job)
        results.append(scored)
    
    # Sort by fit score descending
    results.sort(key=lambda x: x["fit_score"], reverse=True)
    return results


def filter_jobs_by_score(scored_jobs: List[Dict], min_score: int = 65) -> List[Dict]:
    """Filter jobs that meet minimum score threshold."""
    return [job for job in scored_jobs if job["fit_score"] >= min_score and job["decision"] == "apply"]

