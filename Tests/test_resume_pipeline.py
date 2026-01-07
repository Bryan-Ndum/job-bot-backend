import sys
import os

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(ROOT)
if PARENT not in sys.path:
    sys.path.insert(0, PARENT)

from app.services.resume_pipeline import generate_resume_pipeline

print("\n🚀 TESTING RESUME PIPELINE...\n")

job_description = "IT Support Analyst role, troubleshooting, Windows, Azure, network basics."

result = generate_resume_pipeline(job_description)

print("\n=== RESULT ===")
print(f"HTML Path: {result['html_resume']}")
print(f"PDF Path:  {result['pdf_resume']}")
print(f"Cover Letter: {result['cover_letter']}")
print("=================\n")

