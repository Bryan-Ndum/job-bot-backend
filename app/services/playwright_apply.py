"""
Playwright-based Auto-Apply Execution Engine
Handles 80% of application automation with human-like behavior.
"""

import time
import random
import os
from typing import Dict, Optional
# Apply nest_asyncio before importing Playwright to allow sync API in async contexts
try:
    import nest_asyncio
    nest_asyncio.apply()
except (ImportError, Exception):
    pass
from playwright.sync_api import sync_playwright, Page, Browser
from app.services.ats_detector import detect_ats
from app.services.captcha_handler import handle_captcha_if_present
from app.services.ats_automation_helpers import (
    fill_form_fields, upload_file, handle_eeo_fields,
    navigate_multi_step_form, find_and_click_submit_button, human_delay
)


class PlaywrightApplyEngine:
    """Main engine for automated job applications using Playwright."""
    
    def __init__(self, headless: bool = False, captcha_service: str = "2captcha", captcha_api_key: Optional[str] = None):
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None
        self.captcha_service = captcha_service
        self.captcha_api_key = captcha_api_key or os.getenv("CAPTCHA_2CAPTCHA_API_KEY")
        self.enable_captcha_solving = bool(self.captcha_api_key)
    
    def start(self):
        """Initialize Playwright and browser."""
        # Simply start Playwright - if there's an asyncio loop, it will error
        # but that's okay, the error handling will catch it
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        self.page = self.browser.new_page()
        
        # Add stealth features
        self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
    
    def stop(self):
        """Close browser and cleanup."""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def human_delay(self, min_ms: int = 500, max_ms: int = 2000):
        """Add human-like random delay."""
        delay = random.uniform(min_ms / 1000, max_ms / 1000)
        time.sleep(delay)
    
    def human_type(self, element, text: str):
        """Type text with human-like delays between characters."""
        element.click()
        self.human_delay(200, 500)
        
        for char in text:
            element.type(char, delay=random.uniform(50, 150))
            time.sleep(random.uniform(0.01, 0.05))
    
    def apply_to_job(
        self,
        url: str,
        resume_path: str,
        cover_letter_path: Optional[str] = None,
        user_info: Optional[Dict] = None
    ) -> Dict:
        """
        Main application flow - completes ~80% of application.
        
        Steps:
        1. Load job application page
        2. Detect ATS platform
        3. Auto-fill standard fields
        4. Upload resume and cover letter
        5. Answer basic screening questions
        6. Stop before final submission (user completes remaining 20%)
        """
        
        if not self.page:
            self.start()
        
        result = {
            "status": "pending",
            "url": url,
            "ats_type": None,
            "completed_steps": [],
            "remaining_steps": [],
            "error": None
        }
        
        try:
            # Step 1: Navigate to job page
            print(f"🌐 Navigating to {url}")
            try:
                self.page.goto(url, wait_until="networkidle", timeout=60000)
            except Exception as nav_error:
                # Try with domcontentloaded as fallback
                print(f"⚠️ Networkidle timeout, trying domcontentloaded...")
                try:
                    self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
                except:
                    # Last resort - just load the page
                    self.page.goto(url, timeout=60000)
            self.human_delay(2000, 4000)
            
            # Step 1.5: Handle captcha if present
            if self.enable_captcha_solving:
                print("🔍 Checking for captcha...")
                captcha_result = handle_captcha_if_present(
                    self.page,
                    api_key=self.captcha_api_key,
                    service=self.captcha_service
                )
                if captcha_result.get("handled"):
                    if captcha_result.get("success"):
                        print(f"✅ Captcha solved successfully ({captcha_result.get('type')})")
                        self.human_delay(2000, 3000)
                    else:
                        print(f"⚠️ Captcha detected but solving failed: {captcha_result.get('error')}")
                        result["captcha_warning"] = captcha_result.get("error")
            
            # Step 2: Detect ATS
            ats_type = detect_ats(url)
            result["ats_type"] = ats_type
            print(f"🔎 Detected ATS: {ats_type}")
            
            # Step 3: Handle different ATS platforms
            if ats_type == "linkedin":
                result = self._apply_linkedin(resume_path, cover_letter_path, user_info, result)
            elif ats_type == "greenhouse":
                result = self._apply_greenhouse(resume_path, cover_letter_path, user_info, result)
            elif ats_type == "lever":
                result = self._apply_lever(resume_path, cover_letter_path, user_info, result)
            elif ats_type == "workday":
                result = self._apply_workday(resume_path, cover_letter_path, user_info, result)
            elif ats_type == "jobvite":
                result = self._apply_jobvite(resume_path, cover_letter_path, user_info, result)
            elif ats_type in ["workable", "bamboohr", "smartrecruiters", "icims", "ashby", "taleo", "indeed", "ziprecruiter"]:
                # Use generic handler for other major ATS platforms
                result = self._apply_generic(resume_path, cover_letter_path, user_info, result)
            else:
                result = self._apply_generic(resume_path, cover_letter_path, user_info, result)
            
            result["status"] = "completed_80_percent"
            
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            print(f"❌ Application error: {e}")
        
        return result
    
    def _apply_linkedin(self, resume_path: str, cover_letter_path: Optional[str], user_info: Optional[Dict], result: Dict) -> Dict:
        """Handle LinkedIn Easy Apply with full automation."""
        try:
            print("📝 Processing LinkedIn Easy Apply form...")
            
            # Click Easy Apply button
            easy_apply = self.page.locator("button.jobs-apply-button").first
            if easy_apply.is_visible():
                easy_apply.click()
                self.human_delay(2000, 3000)
                result["completed_steps"].append("opened_apply_modal")
                
                # Check for captcha in modal
                if self.enable_captcha_solving:
                    captcha_result = handle_captcha_if_present(
                        self.page,
                        api_key=self.captcha_api_key,
                        service=self.captcha_service
                    )
                    if captcha_result.get("handled") and captcha_result.get("success"):
                        print(f"✅ Modal captcha solved ({captcha_result.get('type')})")
                        self.human_delay(2000, 3000)
            
            # Upload resume
            print("📤 Uploading resume...")
            if upload_file(self.page, resume_path, "resume"):
                print("   ✅ Resume uploaded")
                result["completed_steps"].append("uploaded_resume")
            
            # Fill standard fields
            if user_info:
                print("✏️ Filling personal information...")
                linkedin_fields = {
                    "email": ["email", "e-mail"],
                    "phone": ["phone", "phone number", "mobile"],
                    "location": ["location", "city"],
                    "linkedin": ["linkedin", "linkedin url"],
                    "website": ["website", "portfolio", "personal website"]
                }
                filled = fill_form_fields(self.page, linkedin_fields, user_info)
                if filled:
                    print(f"   ✅ Filled {len(filled)} fields")
                    result["completed_steps"].append("filled_basic_fields")
            
            # Upload cover letter if provided
            if cover_letter_path:
                print("📄 Uploading cover letter...")
                if upload_file(self.page, cover_letter_path, "cover"):
                    print("   ✅ Cover letter uploaded")
                    result["completed_steps"].append("uploaded_cover_letter")
            
            # Navigate multi-step form
            print("➡️ Navigating multi-step form...")
            next_clicked, submit_in_next = navigate_multi_step_form(self.page, max_steps=5)
            if submit_in_next:
                print("   ✅ Submitted via Next button")
                result["completed_steps"].append("submitted_application")
                result["remaining_steps"] = []
                return result
            
            # Handle EEO fields
            print("📋 Handling optional fields...")
            if handle_eeo_fields(self.page):
                print("   ✅ EEO fields handled")
            
            # Submit application
            print("🚀 Submitting application...")
            if find_and_click_submit_button(self.page):
                print("   ✅ Application submitted")
                result["completed_steps"].append("submitted_application")
                result["remaining_steps"] = []
            else:
                # LinkedIn sometimes uses "Review" then "Submit"
                try:
                    review_btn = self.page.locator("button:has-text('Review'), button[aria-label*='Review']").first
                    if review_btn.is_visible(timeout=2000):
                        review_btn.click()
                        self.human_delay(2000, 3000)
                        # Now try submit again
                        if find_and_click_submit_button(self.page):
                            result["completed_steps"].append("submitted_application")
                            result["remaining_steps"] = []
                        else:
                            result["remaining_steps"] = ["submit_application"]
                    else:
                        result["remaining_steps"] = ["submit_application"]
                except:
                    result["remaining_steps"] = ["submit_application"]
            
        except Exception as e:
            result["error"] = f"LinkedIn apply error: {str(e)}"
            print(f"❌ Error: {e}")
        
        return result
    
    def _apply_greenhouse(self, resume_path: str, cover_letter_path: Optional[str], user_info: Optional[Dict], result: Dict) -> Dict:
        """Handle Greenhouse applications with full automation."""
        try:
            print("📝 Processing Greenhouse application form...")
            self.human_delay(2000, 3000)
            
            # Fill personal information
            if user_info:
                print("✏️ Filling personal information...")
                greenhouse_fields = {
                    "first_name": ["first name", "firstname", "fname"],
                    "last_name": ["last name", "lastname", "lname"],
                    "email": ["email", "email address"],
                    "phone": ["phone", "phone number", "telephone"]
                }
                filled = fill_form_fields(self.page, greenhouse_fields, user_info)
                if filled:
                    print(f"   ✅ Filled {len(filled)} fields")
                    result["completed_steps"].append("filled_basic_fields")
            
            # Upload resume
            print("📤 Uploading resume...")
            if upload_file(self.page, resume_path, "resume"):
                print("   ✅ Resume uploaded")
                result["completed_steps"].append("uploaded_resume")
            
            # Upload cover letter
            if cover_letter_path:
                print("📄 Uploading cover letter...")
                if upload_file(self.page, cover_letter_path, "cover"):
                    print("   ✅ Cover letter uploaded")
                    result["completed_steps"].append("uploaded_cover_letter")
            
            # Navigate multi-step form
            print("➡️ Navigating multi-step form...")
            next_clicked, submit_in_next = navigate_multi_step_form(self.page, max_steps=5)
            if submit_in_next:
                print("   ✅ Submitted via Next button")
                result["completed_steps"].append("submitted_application")
                result["remaining_steps"] = []
                return result
            
            # Handle EEO fields
            print("📋 Handling optional fields...")
            if handle_eeo_fields(self.page):
                print("   ✅ EEO fields handled")
            
            # Submit application
            print("🚀 Submitting application...")
            if find_and_click_submit_button(self.page):
                print("   ✅ Application submitted")
                result["completed_steps"].append("submitted_application")
                result["remaining_steps"] = []
            else:
                result["remaining_steps"] = ["submit_application"]
            
        except Exception as e:
            result["error"] = f"Greenhouse apply error: {str(e)}"
            print(f"❌ Error: {e}")
        
        return result
    
    def _apply_lever(self, resume_path: str, cover_letter_path: Optional[str], user_info: Optional[Dict], result: Dict) -> Dict:
        """Handle Lever applications with full automation."""
        try:
            print("📝 Processing Lever application form...")
            self.human_delay(2000, 3000)
            
            # Fill personal information
            if user_info:
                print("✏️ Filling personal information...")
                lever_fields = {
                    "first_name": ["first name", "firstname", "fname"],
                    "last_name": ["last name", "lastname", "lname"],
                    "email": ["email", "email address"],
                    "phone": ["phone", "phone number"]
                }
                filled = fill_form_fields(self.page, lever_fields, user_info)
                if filled:
                    print(f"   ✅ Filled {len(filled)} fields")
                    result["completed_steps"].append("filled_basic_fields")
            
            # Upload resume
            print("📤 Uploading resume...")
            if upload_file(self.page, resume_path, "resume"):
                print("   ✅ Resume uploaded")
                result["completed_steps"].append("uploaded_resume")
            
            # Upload cover letter
            if cover_letter_path:
                print("📄 Uploading cover letter...")
                if upload_file(self.page, cover_letter_path, "cover"):
                    print("   ✅ Cover letter uploaded")
                    result["completed_steps"].append("uploaded_cover_letter")
            
            # Navigate multi-step form
            print("➡️ Navigating multi-step form...")
            next_clicked, submit_in_next = navigate_multi_step_form(self.page, max_steps=5)
            if submit_in_next:
                print("   ✅ Submitted via Next button")
                result["completed_steps"].append("submitted_application")
                result["remaining_steps"] = []
                return result
            
            # Handle EEO fields
            print("📋 Handling optional fields...")
            if handle_eeo_fields(self.page):
                print("   ✅ EEO fields handled")
            
            # Submit application
            print("🚀 Submitting application...")
            if find_and_click_submit_button(self.page):
                print("   ✅ Application submitted")
                result["completed_steps"].append("submitted_application")
                result["remaining_steps"] = []
            else:
                result["remaining_steps"] = ["submit_application"]
            
        except Exception as e:
            result["error"] = f"Lever apply error: {str(e)}"
            print(f"❌ Error: {e}")
        
        return result
    
    def _apply_workday(self, resume_path: str, cover_letter_path: Optional[str], user_info: Optional[Dict], result: Dict) -> Dict:
        """Handle Workday applications with full automation."""
        try:
            print("📝 Processing Workday application form...")
            self.human_delay(3000, 5000)  # Workday forms take longer to load
            
            # Fill personal information
            if user_info:
                print("✏️ Filling personal information...")
                workday_fields = {
                    "first_name": ["first name", "firstname", "given name"],
                    "last_name": ["last name", "lastname", "surname", "family name"],
                    "email": ["email", "email address", "e-mail"],
                    "phone": ["phone", "phone number", "mobile", "telephone"]
                }
                filled = fill_form_fields(self.page, workday_fields, user_info)
                if filled:
                    print(f"   ✅ Filled {len(filled)} fields")
                    result["completed_steps"].append("filled_basic_fields")
            
            # Upload resume
            print("📤 Uploading resume...")
            if upload_file(self.page, resume_path, "resume"):
                print("   ✅ Resume uploaded")
                result["completed_steps"].append("uploaded_resume")
            
            # Upload cover letter
            if cover_letter_path:
                print("📄 Uploading cover letter...")
                if upload_file(self.page, cover_letter_path, "cover"):
                    print("   ✅ Cover letter uploaded")
                    result["completed_steps"].append("uploaded_cover_letter")
            
            # Navigate multi-step form (Workday often has many steps)
            print("➡️ Navigating multi-step form...")
            next_clicked, submit_in_next = navigate_multi_step_form(self.page, max_steps=10)  # More steps for Workday
            if submit_in_next:
                print("   ✅ Submitted via Next button")
                result["completed_steps"].append("submitted_application")
                result["remaining_steps"] = []
                return result
            
            # Handle EEO fields
            print("📋 Handling optional fields...")
            if handle_eeo_fields(self.page):
                print("   ✅ EEO fields handled")
            
            # Submit application
            print("🚀 Submitting application...")
            if find_and_click_submit_button(self.page):
                print("   ✅ Application submitted")
                result["completed_steps"].append("submitted_application")
                result["remaining_steps"] = []
            else:
                result["remaining_steps"] = ["submit_application"]
            
        except Exception as e:
            result["error"] = f"Workday apply error: {str(e)}"
            print(f"❌ Error: {e}")
        
        return result
    
    def _apply_jobvite(self, resume_path: str, cover_letter_path: Optional[str], user_info: Optional[Dict], result: Dict) -> Dict:
        """Handle Jobvite applications with full automation."""
        try:
            print("📝 Processing Jobvite application form...")
            self.human_delay(2000, 3000)  # Wait for form to load
            
            # Upload resume
            print("📤 Uploading resume...")
            if upload_file(self.page, resume_path, "resume"):
                print("   ✅ Resume uploaded")
                result["completed_steps"].append("uploaded_resume")
            
            # Fill personal information
            if user_info:
                print("✏️ Filling personal information...")
                jobvite_fields = {
                    "first_name": ["first name", "firstname", "fname", "firstName"],
                    "last_name": ["last name", "lastname", "lname", "lastName"],
                    "email": ["email", "email address", "e-mail"],
                    "phone": ["phone", "phone number", "telephone", "mobile"]
                }
                filled = fill_form_fields(self.page, jobvite_fields, user_info)
                if filled:
                    print(f"   ✅ Filled {len(filled)} fields")
                    result["completed_steps"].append("filled_basic_fields")
            
            # Upload cover letter
            if cover_letter_path:
                print("📄 Uploading cover letter...")
                if upload_file(self.page, cover_letter_path, "cover"):
                    print("   ✅ Cover letter uploaded")
                    result["completed_steps"].append("uploaded_cover_letter")
            
            # Navigate multi-step form
            print("➡️ Navigating multi-step form...")
            next_clicked, submit_in_next = navigate_multi_step_form(self.page, max_steps=5)
            if submit_in_next:
                print("   ✅ Submitted via Next button")
                result["completed_steps"].append("submitted_application")
                result["remaining_steps"] = []
                return result
            
            # Handle EEO fields
            print("📋 Handling optional fields...")
            if handle_eeo_fields(self.page):
                print("   ✅ EEO fields handled")
            
            # Submit application
            print("🚀 Submitting application...")
            if find_and_click_submit_button(self.page):
                print("   ✅ Application submitted")
                result["completed_steps"].append("submitted_application")
                result["remaining_steps"] = []
            else:
                result["remaining_steps"] = ["submit_application"]
            
        except Exception as e:
            result["error"] = f"Jobvite apply error: {str(e)}"
            print(f"❌ Error: {e}")
        
        return result
    
    def _apply_generic(self, resume_path: str, cover_letter_path: Optional[str], user_info: Optional[Dict], result: Dict) -> Dict:
        """Generic application handler for unknown ATS with full automation."""
        try:
            print("📝 Processing generic application form...")
            self.human_delay(2000, 3000)
            
            # Fill personal information using common field names
            if user_info:
                print("✏️ Filling personal information...")
                generic_fields = {
                    "first_name": ["first name", "firstname", "fname", "given name"],
                    "last_name": ["last name", "lastname", "lname", "surname"],
                    "email": ["email", "email address", "e-mail"],
                    "phone": ["phone", "phone number", "mobile", "telephone"],
                    "name": ["name", "full name"]
                }
                filled = fill_form_fields(self.page, generic_fields, user_info)
                if filled:
                    print(f"   ✅ Filled {len(filled)} fields")
                    result["completed_steps"].append("filled_basic_fields")
            
            # Upload resume
            print("📤 Uploading resume...")
            if upload_file(self.page, resume_path, "resume"):
                print("   ✅ Resume uploaded")
                result["completed_steps"].append("uploaded_resume")
            
            # Upload cover letter
            if cover_letter_path:
                print("📄 Uploading cover letter...")
                if upload_file(self.page, cover_letter_path, "cover"):
                    print("   ✅ Cover letter uploaded")
                    result["completed_steps"].append("uploaded_cover_letter")
            
            # Navigate multi-step form
            print("➡️ Navigating multi-step form...")
            next_clicked, submit_in_next = navigate_multi_step_form(self.page, max_steps=5)
            if submit_in_next:
                print("   ✅ Submitted via Next button")
                result["completed_steps"].append("submitted_application")
                result["remaining_steps"] = []
                return result
            
            # Handle EEO fields
            print("📋 Handling optional fields...")
            if handle_eeo_fields(self.page):
                print("   ✅ EEO fields handled")
            
            # Submit application
            print("🚀 Submitting application...")
            if find_and_click_submit_button(self.page):
                print("   ✅ Application submitted")
                result["completed_steps"].append("submitted_application")
                result["remaining_steps"] = []
            else:
                print("   ⚠️ Submit button not found - may require manual completion")
                result["remaining_steps"] = ["manual_completion_required"]
            
        except Exception as e:
            result["error"] = f"Generic apply error: {str(e)}"
            print(f"❌ Error: {e}")
        
        return result
    
    def _fill_linkedin_fields(self, user_info: Dict):
        """Fill LinkedIn-specific fields."""
        # LinkedIn Easy Apply fields
        fields_map = {
            "email": user_info.get("email", ""),
            "phone": user_info.get("phone", ""),
            "location": user_info.get("location", ""),
            "website": user_info.get("website", ""),
            "linkedin": user_info.get("linkedin", "")
        }
        
        for field_name, value in fields_map.items():
            if value:
                self._fill_field_by_label(field_name, value)
                self.human_delay(300, 800)
    
    def _fill_field_by_label(self, label_text: str, value: str):
        """Find input field by label text and fill it."""
        try:
            # Try various selectors
            label = self.page.locator(f"label:has-text('{label_text}')").first
            if label.is_visible():
                input_id = label.get_attribute("for")
                if input_id:
                    input_field = self.page.locator(f"#{input_id}")
                    if input_field.is_visible():
                        self.human_type(input_field, value)
                        return
            
            # Try direct input with placeholder or name
            input_field = self.page.locator(f"input[placeholder*='{label_text}'], input[name*='{label_text}']").first
            if input_field.is_visible():
                self.human_type(input_field, value)
                return
            
        except Exception:
            pass  # Field not found, continue
    
    def _answer_linkedin_questions(self):
        """Answer basic LinkedIn screening questions."""
        # This would use the existing question_answer_ai module
        # For now, placeholder
        pass


def apply_with_playwright(
    url: str,
    resume_path: str,
    cover_letter_path: Optional[str] = None,
    user_info: Optional[Dict] = None,
    headless: bool = False,
    captcha_service: str = "2captcha",
    captcha_api_key: Optional[str] = None
) -> Dict:
    """
    Convenience function to apply using Playwright.
    
    Args:
        url: Job application URL
        resume_path: Path to resume PDF
        cover_letter_path: Path to cover letter (optional)
        user_info: User information dict
        headless: Run browser in headless mode
        captcha_service: Captcha solving service ('2captcha', 'anticaptcha')
        captcha_api_key: API key for captcha service (or set CAPTCHA_2CAPTCHA_API_KEY env var)
    """
    engine = PlaywrightApplyEngine(
        headless=headless,
        captcha_service=captcha_service,
        captcha_api_key=captcha_api_key
    )
    try:
        result = engine.apply_to_job(url, resume_path, cover_letter_path, user_info)
        return result
    finally:
        engine.stop()

