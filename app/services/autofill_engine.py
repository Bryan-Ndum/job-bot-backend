import time
import re
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException

# Your personal profile for autofill
PROFILE = {
    "full_name": "Bryan Ndum",
    "email": "bryanndum12@gmail.com",
    "linkedin_email": "bryanndum@outlook.com",
    "phone": "9842747193",
    "location": "Clayton, NC",
    "authorized": "Yes",
    "relocate": "Yes",
    "salary_min": "70000",
    "experience_years": "3",
}

def fill_text_field(element, value):
    """Clear and input text safely."""
    try:
        element.clear()
        time.sleep(0.3)
        element.send_keys(value)
        time.sleep(0.4)
        return True
    except Exception:
        return False

def fill_linkedin_fields(driver):
    """Finds and fills fields inside the LinkedIn Easy Apply modal."""
    print("📝 Autofilling LinkedIn fields…")

    # Get all input fields
    inputs = driver.find_elements(By.CSS_SELECTOR, "input")
    textareas = driver.find_elements(By.CSS_SELECTOR, "textarea")

    all_fields = inputs + textareas

    for field in all_fields:
        try:
            aria_label = field.get_attribute("aria-label")
            placeholder = field.get_attribute("placeholder")
            field_id = field.get_attribute("id")
            label_text = aria_label or placeholder or field_id or ""

            label_lower = label_text.lower()

            # Map fields by semantic meaning
            if "email" in label_lower:
                fill_text_field(field, PROFILE["email"])
                
            elif "phone" in label_lower or "mobile" in label_lower:
                fill_text_field(field, PROFILE["phone"])

            elif "city" in label_lower or "location" in label_lower:
                fill_text_field(field, PROFILE["location"])

            elif "name" in label_lower and "first" in label_lower:
                fill_text_field(field, PROFILE["full_name"].split()[0])

            elif "name" in label_lower and "last" in label_lower:
                fill_text_field(field, PROFILE["full_name"].split()[1])

            elif "authorized" in label_lower:
                fill_text_field(field, PROFILE["authorized"])

            elif "relocate" in label_lower:
                fill_text_field(field, PROFILE["relocate"])

            elif "salary" in label_lower:
                fill_text_field(field, PROFILE["salary_min"])

            elif "experience" in label_lower:
                fill_text_field(field, PROFILE["experience_years"])

        except Exception:
            continue

    # Checkboxes
    checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
    for box in checkboxes:
        try:
            driver.execute_script("arguments[0].click();", box)
            time.sleep(0.3)
        except Exception:
            pass

    print("🟢 Autofill complete.")
