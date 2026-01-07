import os
import time
from app.core.supabase_client import get_supabase

# Initialize Supabase client
sb = get_supabase()

# Local folder for screenshots
SCREENSHOT_DIR = "storage/screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def save_screenshot(driver, user_id: str, step_name: str):
    """
    Saves a screenshot locally AND uploads it to Supabase storage.
    Returns the local file path.
    """
    timestamp = int(time.time())
    filename = f"{user_id}_{step_name}_{timestamp}.png"
    local_path = os.path.join(SCREENSHOT_DIR, filename)

    # --------------------------
    # SAVE LOCALLY
    # --------------------------
    try:
        driver.save_screenshot(local_path)
        print(f"📸 Screenshot saved locally → {local_path}")
    except Exception as e:
        print(f"❌ Failed to save screenshot locally: {e}")
        return None

    # --------------------------
    # UPLOAD TO SUPABASE
    # --------------------------
    try:
        with open(local_path, "rb") as f:
            sb.storage.from_("screenshots").upload(
                path=filename,
                file=f,
                file_options={"content-type": "image/png"}
            )
        print(f"☁️ Screenshot uploaded to Supabase → {filename}")
    except Exception as e:
        print(f"⚠️ Supabase upload failed: {e}")

    return local_path
