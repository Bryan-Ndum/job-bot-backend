import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException

def upload_file_input(driver, resume_path):
    """Handles <input type='file'> elements."""
    try:
        file_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
        for input_el in file_inputs:
            try:
                input_el.send_keys(os.path.abspath(resume_path))
                print("📤 Uploaded resume via <input type='file'>")
                time.sleep(3)
                return True
            except:
                continue
    except:
        pass
    return False


def upload_drag_drop(driver, resume_path):
    """Handles drag-drop upload zones used by many ATS systems."""
    try:
        drop_zones = driver.find_elements(By.CSS_SELECTOR, "[data-test-drag-drop], .drag-drop, .upload-dropzone")
        for zone in drop_zones:
            try:
                file_input = driver.execute_script("""
                    var input = document.createElement('input');
                    input.type = 'file';
                    input.style.display = 'none';
                    document.body.appendChild(input);
                    return input;
                """)
                file_input.send_keys(os.path.abspath(resume_path))
                print("📤 Uploaded resume via drag-drop")
                time.sleep(3)
                return True
            except:
                continue
    except:
        pass

    return False


def upload_linkedin_specific(driver, resume_path):
    """LinkedIn-specific upload zone handling."""
    try:
        upload_buttons = driver.find_elements(By.CSS_SELECTOR, "button[aria-label*='Upload'], button[id*='resume']")
        for button in upload_buttons:
            try:
                driver.execute_script("arguments[0].click();", button)
                time.sleep(2)
                return upload_file_input(driver, resume_path)
            except:
                continue
    except:
        pass

    # Try LinkedIn hidden file input
    return upload_file_input(driver, resume_path)


def wait_for_linkedin_upload(driver):
    """Wait until LinkedIn finishes parsing resume."""
    print("⏳ Waiting for resume processing…")
    for _ in range(20):
        try:
            done = driver.find_element(By.CSS_SELECTOR, ".jobs-document-upload__success")
            print("✅ LinkedIn resume upload completed.")
            return True
        except:
            time.sleep(1)
    print("⚠️ LinkedIn resume upload timeout.")
    return False


def upload_resume_linkedin(driver, resume_path):
    """Universal resume uploader with LinkedIn-specific logic."""
    print("📄 Starting resume upload…")

    # Try LinkedIn-specific method
    if upload_linkedin_specific(driver, resume_path):
        wait_for_linkedin_upload(driver)
        return True

    # Try <input type="file">
    if upload_file_input(driver, resume_path):
        wait_for_linkedin_upload(driver)
        return True

    # Try drag-drop
    if upload_drag_drop(driver, resume_path):
        wait_for_linkedin_upload(driver)
        return True

    print("❌ Resume upload failed on all methods.")
    return False


def upload_resume_universal(driver, resume_path):
    """
    Universal uploader for ALL ATS platforms.
    """
    # Try input[type=file]
    if upload_file_input(driver, resume_path):
        return True

    # Try generic drag-drop
    if upload_drag_drop(driver, resume_path):
        return True

    print("❌ Universal resume upload failed.")
    return False
