"""
Playwright Apply using Multiprocessing to avoid asyncio conflicts.
This runs Playwright in a completely separate process.
"""

import multiprocessing
from typing import Dict, Optional
import os
import sys

def _run_playwright_apply_in_process(
    url: str,
    resume_path: str,
    cover_letter_path: Optional[str],
    user_info: Optional[Dict],
    headless: bool,
    captcha_service: str,
    captcha_api_key: Optional[str]
) -> Dict:
    """
    Run Playwright application in a separate process.
    This process has no asyncio loop, so Playwright sync API works.
    """
    # Import here to avoid issues with multiprocessing
    from app.services.playwright_apply import PlaywrightApplyEngine
    
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


def apply_with_playwright_process(
    url: str,
    resume_path: str,
    cover_letter_path: Optional[str] = None,
    user_info: Optional[Dict] = None,
    headless: bool = False,
    captcha_service: str = "2captcha",
    captcha_api_key: Optional[str] = None
) -> Dict:
    """
    Apply to a job using Playwright in a separate thread.
    This avoids asyncio loop conflicts by ensuring the thread has no event loop.
    
    Args:
        url: Job application URL
        resume_path: Path to resume PDF
        cover_letter_path: Path to cover letter (optional)
        user_info: User information dict
        headless: Run browser in headless mode
        captcha_service: Captcha solving service
        captcha_api_key: API key for captcha service
    
    Returns:
        Application result dict
    """
    import threading
    import queue
    import asyncio
    
    result_queue = queue.Queue()
    error_occurred = threading.Event()
    
    def run_in_clean_thread():
        """Run in a thread with no asyncio loop"""
        try:
            # Clear any event loop in this thread
            try:
                # Try to clear thread-local event loop
                thread = threading.current_thread()
                if hasattr(thread, '__dict__'):
                    thread.__dict__.pop('_event_loop', None)
                    thread.__dict__.pop('_asyncio_event_loop', None)
            except Exception:
                pass
            
            # Try to set event loop to None for this thread
            try:
                asyncio.set_event_loop(None)
            except Exception:
                pass
            
            # Now import and run Playwright
            from app.services.playwright_apply import PlaywrightApplyEngine
            
            engine = PlaywrightApplyEngine(
                headless=headless,
                captcha_service=captcha_service,
                captcha_api_key=captcha_api_key
            )
            try:
                result = engine.apply_to_job(url, resume_path, cover_letter_path, user_info)
                result_queue.put(result)
            finally:
                engine.stop()
        except Exception as e:
            error_occurred.set()
            result_queue.put({
                "status": "error",
                "error": str(e)
            })
    
    thread = threading.Thread(target=run_in_clean_thread, daemon=False)
    thread.start()
    thread.join(timeout=300)  # 5 minute timeout
    
    if thread.is_alive():
        return {
            "status": "error",
            "error": "Application thread timed out after 5 minutes"
        }
    
    try:
        result = result_queue.get(timeout=1)
        return result
    except queue.Empty:
        return {
            "status": "error",
            "error": "No result from application thread"
        }

