import sys
import traceback
import os

# -----------------------------------------------------------
# ENSURE PROJECT ROOT IS IMPORTABLE
# -----------------------------------------------------------
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Import main apply function
from app.services.linkedin_apply import linkedin_easy_apply


def run():
    print("\n🔥 LINKEDIN APPLY INTEGRATION TEST 🔥\n")

    # -------------------------------------------------------
    # GET JOB URL
    # -------------------------------------------------------
    job_url = input("Paste LinkedIn job URL: ").strip()
    if not job_url.startswith("https://www.linkedin.com"):
        print("❌ INVALID: Must be a LinkedIn URL")
        return

    # -------------------------------------------------------
    # GET JOB DESCRIPTION
    # -------------------------------------------------------
    print("\nPaste job description (or type 'skip' to auto-generate):")
    jd = input("> ").strip()

    if jd.lower() == "skip":
        jd = "General IT Analyst job description."

    # -------------------------------------------------------
    # SIMULATED USER ID
    # -------------------------------------------------------
    user_id = "bryan_ndum"

    try:
        print("\n🚀 Running LinkedIn Easy Apply...\n")
        result = linkedin_easy_apply(job_url, jd, user_id)

        print("\n========== RESULT ==========")
        print(result)
        print("=============================\n")

    except Exception as e:
        print("\n❌ FATAL ERROR OCCURRED\n")
        print(str(e))
        print(traceback.format_exc())


if __name__ == "__main__":
    run()
