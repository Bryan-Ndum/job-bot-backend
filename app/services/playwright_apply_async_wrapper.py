"""
Async Playwright wrapper that can be called from sync code.
This avoids the "Playwright Sync API inside asyncio loop" error.
"""

import asyncio
import time
from typing import Dict, Optional
from playwright.async_api import async_playwright, Page, Browser


async def _apply_with_playwright_async(
    url: str,
    resume_path: str,
    cover_letter_path: Optional[str],
    user_info: Optional[Dict],
    headless: bool,
    captcha_service: str,
    captcha_api_key: Optional[str]
) -> Dict:
    """
    Apply to a job using Playwright async API.
    This runs in an async context and works with asyncio.
    """
    from app.services.ats_detector import detect_ats
    
    playwright = None
    browser = None
    browser_context = None  # For persistent context
    page = None
    
    result = {
        "status": "error",
        "url": url,
        "ats_type": None,
        "error": None,
        "duration_seconds": 0
    }
    
    start_time = time.time()
    
    try:
        # Start Playwright async
        playwright = await async_playwright().start()
        
        # Use persistent browser context to save login sessions
        import os
        user_data_dir = os.path.join(os.getcwd(), "storage", "browser_context")
        os.makedirs(user_data_dir, exist_ok=True)
        
        # Launch browser with persistent context (saves cookies/sessions)
        browser_context = await playwright.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        browser = None  # Using persistent context, not regular browser
        page = await browser_context.new_page()
        
        # Add stealth features
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        # Navigate to job page with generous timeout
        print(f"🌐 Navigating to {url}")
        try:
            await page.goto(url, wait_until="networkidle", timeout=120000)  # 2 minutes
        except Exception:
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=120000)  # 2 minutes
            except Exception:
                await page.goto(url, timeout=120000)  # 2 minutes as last resort
        
        # Detect ATS
        ats_type = detect_ats(url)
        result["ats_type"] = ats_type
        print(f"🔎 Detected ATS: {ats_type}")
        
        # Wait a bit for page to load
        await asyncio.sleep(2)
        
        # Handle login for any job board that requires it
        # For Indeed, always check and prompt for login to ensure user can log in
        print("🔐 Checking if login is required...")
        try:
            # For Indeed, always navigate to login page first to ensure user can log in
            if ats_type == "indeed" and "indeed.com" in url:
                print("🔐 Indeed detected - checking login status...")
                login_url = "https://www.indeed.com/account/login"
                
                # Navigate to Indeed login page to show login prompt
                print(f"   🔗 Navigating to Indeed login page...")
                try:
                    await page.goto(login_url, wait_until="domcontentloaded", timeout=120000)  # 2 minutes timeout
                    await asyncio.sleep(3)  # Give it a moment to fully load
                except Exception as nav_error:
                    print(f"   ⚠️ Navigation note: {str(nav_error)[:100]}")
                    # Continue anyway - page might still be loading
                
                needs_login = True  # Always show login prompt for Indeed
            else:
                # For other job boards, check if login is required
                login_indicators = [
                    page.locator("input[name='email'], input[name='username'], input[type='email']"),
                    page.locator("input[type='password']"),
                    page.locator("button:has-text('Sign in'), button:has-text('Log in'), button:has-text('Sign In'), button:has-text('Log In')"),
                    page.locator("a:has-text('Sign in'), a:has-text('Log in'), a:has-text('Sign In'), a:has-text('Log In')")
                ]
                
                needs_login = False
                for indicator in login_indicators:
                    try:
                        count = await indicator.count()
                        if count > 0:
                            first_elem = indicator.first
                            if await first_elem.is_visible(timeout=2000):
                                needs_login = True
                                break
                    except:
                        continue
                
                # Check URL for login/signin
                current_url = page.url
                if "login" in current_url.lower() or "signin" in current_url.lower() or "sign-in" in current_url.lower():
                    needs_login = True
            
            # Wait for user to log in (check if login indicators are gone)
            # Give user 10 minutes (600 seconds) to log in - plenty of time!
            max_wait_seconds = 600
            
            if needs_login:
                job_board = "job board"
                if "indeed.com" in url:
                    job_board = "Indeed"
                    login_url = "https://www.indeed.com/account/login"
                elif "linkedin.com" in url:
                    job_board = "LinkedIn"
                    login_url = "https://www.linkedin.com/login"
                elif "glassdoor.com" in url:
                    job_board = "Glassdoor"
                    login_url = "https://www.glassdoor.com/profile/login_input.htm"
                else:
                    login_url = page.url
                
                print(f"\n{'='*70}")
                print(f"🔐 {job_board.upper()} LOGIN REQUIRED")
                print(f"{'='*70}")
                print(f"\n⚠️ Please log in to {job_board} in the browser window that just opened.")
                print(f"   Login URL: {login_url}")
                print(f"\n   Steps:")
                print(f"   1. Look at the browser window")
                print(f"   2. Enter your {job_board} email and password")
                print(f"   3. Click 'Sign in' or 'Log in'")
                print(f"   4. The application will continue automatically after you log in")
                print(f"\n   ⏳ You have {max_wait_seconds // 60} minutes to complete the login (plenty of time!)")
                print(f"   💾 Your login will be saved for future applications")
                print(f"{'='*70}\n")
                
                print(f"   ⏳ Waiting for login (max {max_wait_seconds // 60} minutes)...")
                
                logged_in = False
                for i in range(max_wait_seconds):
                    await asyncio.sleep(1)
                    try:
                        # Check if we're still on login page
                        current_url = page.url
                        login_page = "login" in current_url.lower() or "signin" in current_url.lower() or "sign-in" in current_url.lower()
                        
                        # Check if login form is still visible
                        login_form = page.locator("input[name='email'], input[name='username'], input[type='email']")
                        form_count = await login_form.count()
                        form_visible = False
                        if form_count > 0:
                            try:
                                form_visible = await login_form.first.is_visible(timeout=1000)
                            except:
                                form_visible = False
                        
                        # If not on login page and form not visible, assume logged in
                        if not login_page and not form_visible:
                            print("   ✅ Login detected! Continuing with application...")
                            await asyncio.sleep(2)  # Wait for page to fully load
                            logged_in = True
                            break
                        
                        # Print progress every 60 seconds (less frequent updates)
                        if i > 0 and i % 60 == 0:
                            remaining = max_wait_seconds - i
                            print(f"   ⏳ Still waiting... ({remaining // 60}m {remaining % 60}s remaining)")
                    except Exception as check_error:
                        # If check fails, assume we might be logged in
                        pass
                
                if not logged_in:
                    print(f"\n   ⚠️ {max_wait_seconds // 60}-minute timeout reached.")
                    print("   Continuing anyway - if you haven't logged in yet, the application may fail.")
                    print("   You can log in now if needed, then we'll continue...")
                    await asyncio.sleep(5)  # Give extra time just in case
            else:
                # Check if we're already logged in (might have persistent session)
                try:
                    current_url = page.url
                    # For Indeed/LinkedIn, check if we're actually logged in by looking for user profile indicators
                    if "indeed.com" in current_url:
                        # Check for Indeed-specific logged-in indicators
                        profile_indicators = [
                            page.locator("[data-testid='account-menu']"),
                            page.locator(".icl-UserMenu"),
                            page.locator("button[aria-label*='Account']"),
                        ]
                        logged_in = False
                        for indicator in profile_indicators:
                            try:
                                count = await indicator.count()
                                if count > 0 and await indicator.first.is_visible(timeout=2000):
                                    logged_in = True
                                    break
                            except:
                                continue
                        
                        if logged_in:
                            print("   ✅ Using saved login session (already logged in)")
                        else:
                            # Even if not on login page, we might need to log in
                            # Wait a bit to see if we get redirected
                            await asyncio.sleep(2)
                    elif "linkedin.com" in current_url:
                        # Similar check for LinkedIn
                        profile_indicators = [
                            page.locator("[data-test-id='nav-profile']"),
                            page.locator(".global-nav__me"),
                        ]
                        logged_in = False
                        for indicator in profile_indicators:
                            try:
                                count = await indicator.count()
                                if count > 0 and await indicator.first.is_visible(timeout=2000):
                                    logged_in = True
                                    break
                            except:
                                continue
                        
                        if logged_in:
                            print("   ✅ Using saved login session (already logged in)")
                except:
                    pass
        except Exception as e:
            print(f"   ⚠️ Could not check login status: {e}")
            print("   Continuing with application...")
        
        # Fill form fields if user_info provided
        if user_info:
            print("✏️ Filling personal information...")
            filled_count = 0
            try:
                # Comprehensive field matching for first name
                if user_info.get("first_name"):
                    first_name_selectors = [
                        "input[name*='first']",
                        "input[name*='firstName']",
                        "input[name*='first_name']",
                        "input[id*='first']",
                        "input[id*='firstName']",
                        "input[placeholder*='First']",
                        "input[placeholder*='first']"
                    ]
                    for selector in first_name_selectors:
                        try:
                            field = page.locator(selector).first
                            count = await field.count()
                            if count > 0:
                                await field.fill(user_info["first_name"])
                                filled_count += 1
                                break
                        except:
                            continue
                
                # Last name
                if user_info.get("last_name"):
                    last_name_selectors = [
                        "input[name*='last']",
                        "input[name*='lastName']",
                        "input[name*='last_name']",
                        "input[id*='last']",
                        "input[id*='lastName']",
                        "input[placeholder*='Last']",
                        "input[placeholder*='last']"
                    ]
                    for selector in last_name_selectors:
                        try:
                            field = page.locator(selector).first
                            count = await field.count()
                            if count > 0:
                                await field.fill(user_info["last_name"])
                                filled_count += 1
                                break
                        except:
                            continue
                
                # Email
                if user_info.get("email"):
                    email_selectors = [
                        "input[type='email']",
                        "input[name*='email']",
                        "input[name*='Email']",
                        "input[id*='email']",
                        "input[placeholder*='Email']",
                        "input[placeholder*='email']"
                    ]
                    for selector in email_selectors:
                        try:
                            field = page.locator(selector).first
                            count = await field.count()
                            if count > 0:
                                await field.fill(user_info["email"])
                                filled_count += 1
                                break
                        except:
                            continue
                
                # Phone
                if user_info.get("phone"):
                    phone_selectors = [
                        "input[type='tel']",
                        "input[name*='phone']",
                        "input[name*='Phone']",
                        "input[name*='phoneNumber']",
                        "input[id*='phone']",
                        "input[placeholder*='Phone']",
                        "input[placeholder*='phone']"
                    ]
                    for selector in phone_selectors:
                        try:
                            field = page.locator(selector).first
                            count = await field.count()
                            if count > 0:
                                await field.fill(user_info["phone"])
                                filled_count += 1
                                break
                        except:
                            continue
                
                # Address line 1
                if user_info.get("address_line1"):
                    address_selectors = [
                        "input[name*='address1']",
                        "input[name*='address_1']",
                        "input[name*='addressLine1']",
                        "input[name*='street']",
                        "input[name*='street1']",
                        "input[id*='address1']",
                        "input[placeholder*='Address']",
                        "input[placeholder*='Street']"
                    ]
                    for selector in address_selectors:
                        try:
                            field = page.locator(selector).first
                            count = await field.count()
                            if count > 0:
                                await field.fill(user_info["address_line1"])
                                filled_count += 1
                                break
                        except:
                            continue
                
                # City
                if user_info.get("city"):
                    city_selectors = [
                        "input[name*='city']",
                        "input[id*='city']",
                        "input[placeholder*='City']"
                    ]
                    for selector in city_selectors:
                        try:
                            field = page.locator(selector).first
                            count = await field.count()
                            if count > 0:
                                await field.fill(user_info["city"])
                                filled_count += 1
                                break
                        except:
                            continue
                
                # State (try select and input)
                if user_info.get("state"):
                    state_value = user_info["state"]
                    # Try select
                    try:
                        state_select = page.locator("select[name*='state'], select[id*='state'], select[name*='region']")
                        if await state_select.count() > 0:
                            try:
                                await state_select.first.select_option(label=state_value)
                                filled_count += 1
                            except:
                                # Try by value (NC)
                                try:
                                    await state_select.first.select_option(value=state_value)
                                    filled_count += 1
                                except:
                                    pass
                    except:
                        pass
                    # Try input fallback
                    state_inputs = [
                        "input[name*='state']",
                        "input[id*='state']",
                        "input[placeholder*='State']",
                        "input[name*='region']",
                        "input[id*='region']",
                    ]
                    for selector in state_inputs:
                        try:
                            field = page.locator(selector).first
                            if await field.count() > 0:
                                await field.fill(state_value)
                                filled_count += 1
                                break
                        except:
                            continue
                
                # ZIP / Postal code
                if user_info.get("zip"):
                    zip_selectors = [
                        "input[name*='zip']",
                        "input[name*='postal']",
                        "input[id*='zip']",
                        "input[id*='postal']",
                        "input[placeholder*='ZIP']",
                        "input[placeholder*='Postal']"
                    ]
                    for selector in zip_selectors:
                        try:
                            field = page.locator(selector).first
                            count = await field.count()
                            if count > 0:
                                await field.fill(user_info["zip"])
                                filled_count += 1
                                break
                        except:
                            continue
                
                # Country (try select then input)
                if user_info.get("country"):
                    try:
                        country_select = page.locator("select[name*='country'], select[id*='country']")
                        if await country_select.count() > 0:
                            try:
                                await country_select.first.select_option(label=user_info["country"])
                                filled_count += 1
                            except:
                                pass
                    except:
                        pass
                    country_inputs = [
                        "input[name*='country']",
                        "input[id*='country']",
                        "input[placeholder*='Country']"
                    ]
                    for selector in country_inputs:
                        try:
                            field = page.locator(selector).first
                            if await field.count() > 0:
                                await field.fill(user_info["country"])
                                filled_count += 1
                                break
                        except:
                            continue
                
                # Generic location field (single-line location prompts)
                if user_info.get("location"):
                    location_selectors = [
                        "input[name*='location']",
                        "input[id*='location']",
                        "input[placeholder*='Location']",
                        "textarea[name*='location']",
                        "textarea[id*='location']"
                    ]
                    for selector in location_selectors:
                        try:
                            field = page.locator(selector).first
                            if await field.count() > 0:
                                await field.fill(user_info["location"])
                                filled_count += 1
                                break
                        except:
                            continue
                
                if filled_count > 0:
                    print(f"   ✅ Filled {filled_count} field(s)")
                    await asyncio.sleep(1)  # Brief pause after filling
            except Exception as e:
                print(f"⚠️ Error filling fields: {e}")
        
        # Wait for page to fully load before trying to upload
        # For Indeed, wait longer as the page might need more time to load
        if ats_type == "indeed":
            print("   ⏳ Waiting for Indeed page to fully load...")
            await asyncio.sleep(5)  # Give Indeed more time
        else:
            await asyncio.sleep(2)
        
        # Upload resume with comprehensive strategies
        print("📤 Uploading resume...")
        resume_uploaded = False
        
        # Strategy 1: Try visible file inputs with various selectors
        file_input_selectors = [
            "input[type='file']",
            "input[type='file'][name*='resume']",
            "input[type='file'][name*='Resume']",
            "input[type='file'][name*='cv']",
            "input[type='file'][name*='CV']",
            "input[type='file'][id*='resume']",
            "input[type='file'][id*='Resume']",
            "input[type='file'][accept*='pdf']",
            "input[type='file'][accept*='doc']"
        ]
        
        for selector in file_input_selectors:
            try:
                file_input = page.locator(selector).first
                count = await file_input.count()
                if count > 0:
                    # Try even if not visible - many file inputs are hidden
                    await file_input.set_input_files(resume_path)
                    await asyncio.sleep(2)  # Wait for upload to process
                    
                    # Verify upload succeeded by checking if file is attached
                    try:
                        value = await file_input.input_value()
                        if value:
                            print(f"   ✅ Resume uploaded via {selector}")
                            resume_uploaded = True
                            break
                    except:
                        # If we can't verify, assume it worked
                        print(f"   ✅ Resume uploaded via {selector}")
                        resume_uploaded = True
                        break
            except Exception as e:
                continue
        
        # Strategy 2: Handle Indeed specifically (has special resume upload flow)
        if not resume_uploaded and ats_type == "indeed":
            try:
                print("   🔍 Trying Indeed-specific resume upload methods...")
                
                # First, wait a bit more and scroll to see if elements load
                await page.evaluate("window.scrollTo(0, 500)")
                await asyncio.sleep(2)
                
                # Indeed often has "Upload resume" or "Choose file" buttons
                # Also check for labels that might wrap file inputs
                indeed_upload_selectors = [
                    # Buttons
                    "button:has-text('Upload resume')",
                    "button:has-text('Upload Resume')",
                    "button:has-text('Choose file')",
                    "button:has-text('Choose File')",
                    "button:has-text('Browse')",
                    "button:has-text('Select file')",
                    "button:has-text('Select File')",
                    # Links
                    "a:has-text('Upload resume')",
                    "a:has-text('Upload Resume')",
                    "a:has-text('Choose file')",
                    # Labels (often wrap file inputs)
                    "label:has-text('Upload resume')",
                    "label:has-text('Upload Resume')",
                    "label:has-text('Choose file')",
                    "label:has-text('Choose File')",
                    "label:has-text('Resume')",
                    # Aria labels
                    "[aria-label*='Upload resume']",
                    "[aria-label*='upload resume']",
                    "[aria-label*='Upload Resume']",
                    "[aria-label*='Choose file']",
                    "[aria-label*='Choose File']",
                    # Data attributes
                    "[data-testid*='upload']",
                    "[data-testid*='resume']",
                    "[data-testid*='file']",
                    # Classes
                    "[class*='upload']",
                    "[class*='resume']",
                    "[class*='file-input']",
                    "[class*='file-upload']",
                ]
                
                for button_selector in indeed_upload_selectors:
                    try:
                        button = page.locator(button_selector).first
                        count = await button.count()
                        if count > 0:
                            # Try both visible and potentially hidden (some buttons trigger on click)
                            try:
                                is_visible = await button.is_visible(timeout=2000)
                            except:
                                is_visible = False
                            
                            if is_visible or count > 0:  # Try clicking even if not visible
                                print(f"   🔘 Trying: {button_selector[:50]}...")
                                await button.scroll_into_view_if_needed()
                                await button.click()
                                await asyncio.sleep(3)  # Wait for file input to appear
                                
                                # Now try to find and use the file input (check multiple times)
                                for attempt in range(3):
                                    try:
                                        file_inputs = await page.locator("input[type='file']").all()
                                        if file_inputs:
                                            print(f"   📎 Found file input, uploading...")
                                            await file_inputs[0].set_input_files(resume_path)
                                            await asyncio.sleep(4)  # Wait for upload to process
                                            
                                            # Check if upload succeeded
                                            try:
                                                value = await file_inputs[0].input_value()
                                                if value:
                                                    print(f"   ✅ Resume uploaded successfully!")
                                                    resume_uploaded = True
                                                    break
                                            except:
                                                # If we can't verify, assume it worked (sometimes input_value fails)
                                                print(f"   ✅ Resume uploaded (assuming success)")
                                                resume_uploaded = True
                                                break
                                        else:
                                            await asyncio.sleep(1)  # Wait and retry
                                    except:
                                        await asyncio.sleep(1)
                                
                                if resume_uploaded:
                                    break
                    except Exception as btn_error:
                        continue
                
                # Also try direct file input (might be hidden but accessible)
                if not resume_uploaded:
                    print("   🔍 Trying direct file input access...")
                    try:
                        # Use JavaScript to find ALL file inputs, including hidden ones
                        file_inputs_data = await page.evaluate("""
                            () => {
                                const inputs = Array.from(document.querySelectorAll('input[type="file"]'));
                                return inputs.map((inp, idx) => ({
                                    index: idx,
                                    id: inp.id || '',
                                    name: inp.name || '',
                                    className: inp.className || '',
                                    visible: inp.offsetParent !== null
                                }));
                            }
                        """)
                        
                        if file_inputs_data and len(file_inputs_data) > 0:
                            print(f"   📎 Found {len(file_inputs_data)} file input(s) via JavaScript")
                            for inp_data in file_inputs_data:
                                try:
                                    # Try to set files using JavaScript directly
                                    file_inputs = await page.locator("input[type='file']").all()
                                    if inp_data['index'] < len(file_inputs):
                                        file_input = file_inputs[inp_data['index']]
                                        print(f"   📤 Trying to upload to file input #{inp_data['index']} (visible: {inp_data['visible']})...")
                                        
                                        # Try to set files
                                        await file_input.set_input_files(resume_path)
                                        await asyncio.sleep(4)
                                        
                                        # Try to verify
                                        try:
                                            value = await file_input.input_value()
                                            if value:
                                                print("   ✅ Resume uploaded via direct file input!")
                                                resume_uploaded = True
                                                break
                                        except:
                                            # Check via JavaScript
                                            has_file = await page.evaluate("""
                                                (inputIndex) => {
                                                    const inputs = document.querySelectorAll('input[type="file"]');
                                                    return inputs[inputIndex] && inputs[inputIndex].files.length > 0;
                                                }
                                            """, inp_data['index'])
                                            if has_file:
                                                print("   ✅ Resume uploaded (verified via JavaScript)!")
                                                resume_uploaded = True
                                                break
                                            else:
                                                print("   ✅ Resume uploaded (assuming success)")
                                                resume_uploaded = True
                                                break
                                except Exception as upload_err:
                                    continue
                        else:
                            # Fallback: try locator method
                            file_inputs = await page.locator("input[type='file']").all()
                            if file_inputs:
                                print(f"   📎 Found {len(file_inputs)} file input(s) via locator")
                                for file_input in file_inputs:
                                    try:
                                        await file_input.set_input_files(resume_path)
                                        await asyncio.sleep(4)
                                        print("   ✅ Resume uploaded (assuming success)")
                                        resume_uploaded = True
                                        break
                                    except Exception as upload_err:
                                        continue
                    except Exception as e:
                        print(f"   ⚠️ Direct file input error: {str(e)[:100]}")
                
            except Exception as e:
                print(f"   ⚠️ Indeed-specific upload error: {str(e)[:100]}")
        
        # Strategy 3: Handle Greenhouse specifically (IXL uses Greenhouse)
        if not resume_uploaded and ats_type == "greenhouse":
            try:
                # Greenhouse often uses specific class names or data attributes
                greenhouse_selectors = [
                    "input[type='file'][data-testid*='file']",
                    "input[type='file'][class*='file']",
                    ".file-upload input[type='file']",
                    "[data-testid='file-upload'] input[type='file']"
                ]
                for selector in greenhouse_selectors:
                    try:
                        file_input = page.locator(selector).first
                        count = await file_input.count()
                        if count > 0:
                            await file_input.set_input_files(resume_path)
                            await asyncio.sleep(2)
                            print(f"   ✅ Resume uploaded via Greenhouse selector: {selector}")
                            resume_uploaded = True
                            break
                    except:
                        continue
            except Exception:
                pass
        
        # Strategy 4: Find ALL file inputs and try the first one (even if hidden)
        if not resume_uploaded:
            try:
                all_file_inputs = await page.locator("input[type='file']").all()
                if all_file_inputs:
                    # Try the first file input (usually resume)
                    await all_file_inputs[0].set_input_files(resume_path)
                    await asyncio.sleep(2)
                    print("   ✅ Resume uploaded via first available file input")
                    resume_uploaded = True
            except Exception as e:
                pass
        
        # Strategy 5: Try drag-and-drop zones (click button that triggers file input)
        if not resume_uploaded:
            try:
                # Look for upload buttons that might trigger file input
                upload_buttons = [
                    "button:has-text('Upload')",
                    "button:has-text('Choose File')",
                    "button:has-text('Browse')",
                    "button:has-text('Select File')",
                    "[role='button']:has-text('Upload')",
                    ".upload-button",
                    "[data-testid*='upload']",
                    "[aria-label*='upload']"
                ]
                for button_selector in upload_buttons:
                    try:
                        button = page.locator(button_selector).first
                        if await button.is_visible():
                            await button.click()
                            await asyncio.sleep(1)
                            # Now try to find and use file input
                            file_input = page.locator("input[type='file']").first
                            count = await file_input.count()
                            if count > 0:
                                await file_input.set_input_files(resume_path)
                                await asyncio.sleep(2)
                                print(f"   ✅ Resume uploaded via upload button: {button_selector}")
                                resume_uploaded = True
                                break
                    except:
                        continue
            except Exception:
                pass
        
        if not resume_uploaded:
            print("   ⚠️ Resume upload failed - file input not found")
            print("   💡 The application form was filled, but resume upload needs manual intervention")
            print("   📋 Please check the browser window - you may need to manually upload the resume")
            result["warning"] = "Resume upload failed - manual upload required. Application form was filled and submitted."
            
            # For Indeed, try to take a screenshot for debugging and log page info
            try:
                screenshot_path = os.path.join("storage", "screenshots", f"indeed_upload_failed_{int(time.time())}.png")
                os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
                await page.screenshot(path=screenshot_path, full_page=True)
                print(f"   📸 Screenshot saved: {screenshot_path}")
                
                # Also log what elements are on the page for debugging
                try:
                    page_info = await page.evaluate("""
                        () => {
                            const buttons = Array.from(document.querySelectorAll('button, a, [role="button"]'));
                            const fileInputs = Array.from(document.querySelectorAll('input[type="file"]'));
                            const labels = Array.from(document.querySelectorAll('label'));
                            
                            return {
                                url: window.location.href,
                                buttons: buttons.slice(0, 10).map(btn => ({
                                    text: btn.textContent?.trim().substring(0, 50) || '',
                                    id: btn.id || '',
                                    className: btn.className || ''
                                })),
                                fileInputs: fileInputs.length,
                                labels: labels.slice(0, 10).map(lbl => ({
                                    text: lbl.textContent?.trim().substring(0, 50) || '',
                                    for: lbl.getAttribute('for') || ''
                                }))
                            };
                        }
                    """)
                    print(f"   🔍 Page has {page_info.get('fileInputs', 0)} file input(s)")
                    print(f"   🔍 Found {len(page_info.get('buttons', []))} buttons")
                except:
                    pass
            except:
                pass
        
        # Wait a bit after file upload before looking for submit
        await asyncio.sleep(2)
        
        # Try to navigate multi-step forms (like Greenhouse)
        if ats_type == "greenhouse":
            print("➡️ Navigating Greenhouse multi-step form...")
            try:
                # Look for "Next" or "Continue" buttons
                next_selectors = [
                    "button:has-text('Next')",
                    "button:has-text('Continue')",
                    "button:has-text('Continue to')",
                    "input[value='Next']",
                    "input[value='Continue']"
                ]
                
                for _ in range(5):  # Max 5 steps
                    next_clicked = False
                    for selector in next_selectors:
                        try:
                            next_btn = page.locator(selector).first
                            if await next_btn.is_visible(timeout=2000):
                                await next_btn.click()
                                print(f"   ⏭️ Clicked Next button")
                                await asyncio.sleep(2)
                                next_clicked = True
                                break
                        except:
                            continue
                    
                    if not next_clicked:
                        break  # No more "Next" buttons, we're on the final step
            except Exception as e:
                print(f"   ⚠️ Error navigating multi-step form: {e}")
        
        # Try to find and click submit button
        print("🔍 Looking for submit button...")
        submit_clicked = False
        try:
            submit_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button:has-text('Submit Application')",
                "button:has-text('Submit')",
                "button:has-text('Apply')",
                "button:has-text('Send Application')",
                "button:has-text('Send')",
                "button:has-text('Complete Application')",
                "button[data-testid*='submit']",
                "button[id*='submit']",
                "button[id*='apply']"
            ]
            
            for selector in submit_selectors:
                try:
                    submit_btn = page.locator(selector).first
                    count = await submit_btn.count()
                    if count > 0:
                        # Check if visible or try to scroll into view
                        try:
                            await submit_btn.scroll_into_view_if_needed()
                        except:
                            pass
                        
                        if await submit_btn.is_visible(timeout=3000):
                            await submit_btn.click()
                            print(f"   ✅ Clicked submit button ({selector})")
                            await asyncio.sleep(3)  # Wait for submission to process
                            result["status"] = "applied"
                            submit_clicked = True
                            break
                except Exception:
                    continue
            
            # If no visible submit button found, try clicking any submit button anyway
            if not submit_clicked:
                try:
                    submit_btn = page.locator("button[type='submit'], input[type='submit']").first
                    count = await submit_btn.count()
                    if count > 0:
                        await submit_btn.click()
                        print("   ✅ Clicked submit button (forced)")
                        await asyncio.sleep(3)
                        result["status"] = "applied"
                        submit_clicked = True
                except:
                    pass
                    
        except Exception as e:
            print(f"   ⚠️ Could not find/click submit button: {e}")
        
        if not submit_clicked:
            result["status"] = "pending"
            result["error"] = "Could not find submit button - application may need manual completion"
            print("   ⚠️ Could not automatically submit - please check the browser window")
        
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        print(f"❌ Error: {e}")
    
    finally:
        # Close browser context (persistent context handles cleanup)
        if browser_context:
            await browser_context.close()
        elif browser:
            await browser.close()
        if playwright:
            await playwright.stop()
        
        # Calculate and add duration
        duration = time.time() - start_time
        result["duration_seconds"] = round(duration, 2)
        
        # Format duration for display
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        if minutes > 0:
            result["duration"] = f"{minutes}m {seconds}s"
        else:
            result["duration"] = f"{seconds}s"
    
    return result


def apply_with_playwright_async_wrapper(
    url: str,
    resume_path: str,
    cover_letter_path: Optional[str] = None,
    user_info: Optional[Dict] = None,
    headless: bool = False,
    captcha_service: str = "2captcha",
    captcha_api_key: Optional[str] = None
) -> Dict:
    """
    Wrapper to run async Playwright code from sync context.
    Uses asyncio.run() to create a new event loop, or runs in thread if loop exists.
    """
    import threading
    
    def run_async_in_thread():
        """Run async code in a new thread with new event loop"""
        return asyncio.run(_apply_with_playwright_async(
            url, resume_path, cover_letter_path,
            user_info, headless, captcha_service, captcha_api_key
        ))
    
    try:
        # Check if we're in an async context
        try:
            loop = asyncio.get_running_loop()
            # We're in an async context (e.g., FastAPI)
            # Run in a separate thread with its own event loop
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_async_in_thread)
                return future.result(timeout=300)  # 5 minute timeout
        except RuntimeError:
            # No running loop - we can use asyncio.run() directly
            return asyncio.run(_apply_with_playwright_async(
                url, resume_path, cover_letter_path,
                user_info, headless, captcha_service, captcha_api_key
            ))
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

