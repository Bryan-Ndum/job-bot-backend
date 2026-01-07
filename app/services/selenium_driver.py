import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import os
import time

CHROME_PROFILE_PATH = r"C:\Users\bryan\AppData\Local\Google\Chrome\User Data\Default"

def create_driver(headless=False):
    options = uc.ChromeOptions()

    # Use your real Chrome profile
    options.add_argument(f"user-data-dir={os.path.dirname(CHROME_PROFILE_PATH)}")
    options.add_argument(f"profile-directory={os.path.basename(CHROME_PROFILE_PATH)}")

    # Disable automation flags
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--start-maximized")
    options.add_argument("--no-first-run")

    # Headless mode optional
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")

    # Faster execution
    prefs = {
        "profile.default_content_setting_values.notifications": 2,
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False
    }
    options.add_experimental_option("prefs", prefs)

    print("🚀 Launching Chrome in stealth mode…")
    driver = uc.Chrome(options=options)

    time.sleep(3)
    print("🟢 Chrome launched successfully with your profile")

    return driver
