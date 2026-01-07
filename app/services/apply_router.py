from app.services.ats_detector import detect_ats
from app.services.api_apply import apply_via_api
from app.services.selenium_apply import apply_via_selenium

ATS_API_SUPPORTED = [
    "greenhouse",
    "lever",
    "workable",
    "bamboohr",
    "ashby"
]

def apply_to_job(url: str, resume_path: str):
    ats = detect_ats(url)

    print(f"🔎 Detected ATS: {ats}")

    # Use API if supported
    if ats in ATS_API_SUPPORTED:
        print("⚡ Using API method")
        return apply_via_api(url, ats, resume_path)

    # Otherwise use Selenium
    print("🖥 Using Selenium automation")
    return apply_via_selenium(url, ats, resume_path)
