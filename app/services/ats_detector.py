import re

ATS_PATTERNS = {
    "greenhouse": r"(greenhouse\.io|boards\.greenhouse\.io|boards-api\.greenhouse\.io)",
    "lever": r"lever\.co",
    "workable": r"apply\.workable\.com",
    "workday": r"myworkdayjobs\.com",
    "taleo": r"taleo\.net",
    "bamboohr": r"bamboohr\.com",
    "smartrecruiters": r"smartrecruiters\.com",
    "icims": r"icims\.com",
    "ashby": r"jobs\.ashbyhq\.com",
    "indeed": r"indeed\.com",
    "linkedin": r"linkedin\.com",
    "ziprecruiter": r"ziprecruiter\.com",
    "jobvite": r"jobvite\.com",
    "greenhouse_apply": r"gh_jid"  # Greenhouse job ID pattern (like IXL's URL)
}

def detect_ats(url: str):
    url_lower = url.lower()
    
    # Check for Greenhouse job ID pattern first (e.g., gh_jid parameter)
    if re.search(r"gh_jid", url_lower):
        return "greenhouse"

    for ats, pattern in ATS_PATTERNS.items():
        if ats == "greenhouse_apply":  # Skip this, already checked above
            continue
        if re.search(pattern, url_lower):
            return ats

    return "unknown"
