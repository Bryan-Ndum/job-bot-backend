import time
import traceback
from selenium.webdriver.common.by import By

from app.services.selenium_driver import create_driver
from app.services.autofill_engine import fill_linkedin_fields
from app.services.question_answer_ai import answer_question
from app.services.screenshot_service import save_screenshot

from app.services.resume_pipeline import generate_resume_pipeline
from app.services.resume_upload import upload_resume_linkedin, upload_resume_universal

from app.core.supabase_client import supabase


def upload_cover_letter_if_exists(driver, cover_letter_path):
    """
    Uploads a cover letter ONLY if LinkedIn displays a cover letter upload field.
    Does nothing silently if field is not found.
    """

    try:
        upload_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
        for inp in upload_inputs:
            name = inp.get_attribute("name") or ""
            aria_label = inp.get_attribute("aria-label") or ""

            if "cover" in name.lower() or "cover" in aria_label.lower():
                print("📨 Uploading cover letter…")
                inp.send_keys(cover_letter_path)
                time.sleep(2)
                return True

        print("ℹ️ No cover letter upload field detected. Skipping.")
        return False

    except Exception:
        print("⚠️ Could not upload cover letter.")
        return False


def linkedin_easy_apply(url: str, job_description: str, user_id: str):
    """
    FULL LINKEDIN EASY APPLY WORKFLOW:
    1. Generate tailored resume (+ cover letter)
    2. Launch Chrome (stealth)
    3. Upload resume
    4. Upload cover letter (if field exists)
    5. Auto-fill fields
    6. AI-driven question answers
    7. Navigate multi-step modal
    8. Submit application
    9. Save screenshots + Supabase log
    """

    print("🎯 Starting LinkedIn Easy Apply workflow…")

    # ------------------------------------------------------
    # STEP 1 — Generate tailored resume + cover letter
    # ------------------------------------------------------
    print("📌 Generating tailored resume and cover letter…")
    resume_info = generate_resume_pipeline(job_description)

    resume_path = resume_info["pdf_resume"]
    cover_letter_path = resume_info["cover_letter"]

    print(f"📄 Resume saved → {resume_path}")
    print(f"✉️ Cover letter saved → {cover_letter_path}")

    # ------------------------------------------------------
    # STEP 2 — Launch Chrome
    # ------------------------------------------------------
    driver = create_driver(headless=False)
    result = {"status": "failed", "url": url}

    try:
        print(f"🌐 Navigating to job page → {url}")
        driver.get(url)
        time.sleep(4)

        # ------------------------------------------------------
        # STEP 3 — Locate & click “Easy Apply”
        # ------------------------------------------------------
        try:
            easy_apply_button = driver.find_element(By.CSS_SELECTOR, "button.jobs-apply-button")
        except:
            print("❌ No Easy Apply button found.")
            save_screenshot(driver, user_id, "no_easy_apply")
            return {"error": "No Easy Apply button"}

        print("🟣 Opening Easy Apply modal…")
        easy_apply_button.click()
        time.sleep(3)

        # ------------------------------------------------------
        # STEP 4 — Upload Resume
        # ------------------------------------------------------
        print("📤 Uploading resume…")
        uploaded = upload_resume_linkedin(driver, resume_path)

        if not uploaded:
            print("⚠️ LinkedIn resume upload failed. Trying universal upload…")
            upload_resume_universal(driver, resume_path)

        time.sleep(3)

        # ------------------------------------------------------
        # STEP 5 — Upload Cover Letter if LinkedIn exposes the field
        # ------------------------------------------------------
        upload_cover_letter_if_exists(driver, cover_letter_path)

        # ------------------------------------------------------
        # MAIN APPLICATION LOOP
        # ------------------------------------------------------
        while True:
            save_screenshot(driver, user_id, "step")

            # Autofill fields
            fill_linkedin_fields(driver)

            # AI-driven question answering
            answer_question(driver)

            # Continue → Next step
            try:
                next_btn = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Continue to next step']")
                next_btn.click()
                print("➡️ Continue…")
                time.sleep(2)
                continue
            except:
                pass

            # Review
            try:
                review_btn = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Review your application']")
                review_btn.click()
                print("📝 Reviewing application…")
                time.sleep(2)
                continue
            except:
                pass

            # Submit
            try:
                submit_btn = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Submit application']")
                submit_btn.click()
                print("🎉 APPLICATION SUBMITTED SUCCESSFULLY!")
                save_screenshot(driver, user_id, "submitted")

                # Log to supabase
                supabase.table("applications").insert({
                    "user_id": user_id,
                    "url": url,
                    "job_description": job_description,
                    "resume_used": resume_path,
                    "cover_letter_used": cover_letter_path,
                    "status": "submitted"
                }).execute()

                result["status"] = "submitted"
                result["resume"] = resume_path
                break

            except:
                print("❗ Submit not available yet — re-checking UI…")
                time.sleep(2)
                continue

    except Exception as e:
        print("❌ LINKEDIN APPLY ERROR:", e)
        print(traceback.format_exc())
        save_screenshot(driver, user_id, "error")
        result["error"] = str(e)

    finally:
        driver.quit()

    return result
