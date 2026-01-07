"""
Shared ATS Automation Helper Functions
Common utilities for all ATS platforms.
"""

import time
import random
from typing import Dict, Optional, List
from playwright.sync_api import Page


def human_delay(min_ms: int = 500, max_ms: int = 2000):
    """Add human-like random delay."""
    delay = random.uniform(min_ms / 1000, max_ms / 1000)
    time.sleep(delay)


def fill_form_fields(page: Page, field_mappings: Dict[str, List[str]], user_info: Dict) -> List[str]:
    """
    Fill form fields using multiple selector strategies.
    
    Args:
        page: Playwright page object
        field_mappings: Dict mapping field_key to list of label variants
        user_info: Dict with user information
    
    Returns:
        List of successfully filled field names
    """
    filled_fields = []
    
    for field_key, label_variants in field_mappings.items():
        value = user_info.get(field_key, "")
        if not value:
            continue
        
        for label_variant in label_variants:
            try:
                # Strategy 1: Find by label text
                label = page.locator(f"label:has-text('{label_variant}')").first
                if label.is_visible(timeout=1000):
                    input_id = label.get_attribute("for")
                    if input_id:
                        input_field = page.locator(f"#{input_id}")
                    else:
                        input_field = label.locator("..").locator("input, textarea, select").first
                    
                    if input_field.is_visible():
                        input_field.fill(value)
                        filled_fields.append(field_key)
                        human_delay(300, 600)
                        break
            except:
                pass
            
            # Strategy 2: Direct input search
            try:
                input_field = page.locator(
                    f"input[name*='{field_key}'], input[id*='{field_key}'], "
                    f"input[placeholder*='{label_variant}'], "
                    f"textarea[name*='{field_key}'], select[name*='{field_key}']"
                ).first
                if input_field.is_visible(timeout=500):
                    input_field.fill(value)
                    filled_fields.append(field_key)
                    human_delay(300, 600)
                    break
            except:
                continue
    
    return filled_fields


def upload_file(page: Page, file_path: str, field_label: str = "resume") -> bool:
    """
    Upload file using multiple strategies.
    
    Args:
        page: Playwright page object
        file_path: Path to file to upload
        field_label: Label to identify the upload field (e.g., "resume", "cover")
    
    Returns:
        True if upload successful
    """
    try:
        # Strategy 1: Find by name/aria-label containing field_label
        selectors = [
            f"input[type='file'][name*='{field_label}']",
            f"input[type='file'][aria-label*='{field_label}']",
            f"input[type='file']#{field_label}",
            "input[type='file']"
        ]
        
        for selector in selectors:
            try:
                file_input = page.locator(selector).first
                if file_input.is_visible(timeout=1000):
                    file_input.set_input_files(file_path)
                    human_delay(1500, 2500)
                    return True
            except:
                continue
        
        # Strategy 2: Find all file inputs and use first/second based on label
        file_inputs = page.locator("input[type='file']").all()
        if file_inputs:
            # For resume, use first; for cover letter, use second
            index = 0 if "resume" in field_label.lower() else 1
            if index < len(file_inputs):
                file_inputs[index].set_input_files(file_path)
                human_delay(1500, 2500)
                return True
        
        return False
    except Exception as e:
        print(f"   ⚠️ File upload error: {e}")
        return False


def handle_eeo_fields(page: Page) -> bool:
    """
    Handle EEO/voluntary disclosure fields by selecting "Decline to answer" options.
    
    Returns:
        True if any EEO fields were handled
    """
    handled = False
    
    try:
        # Find select dropdowns for EEO fields
        eeo_selects = page.locator("select[name*='eeo'], select[name*='race'], select[name*='gender'], select[name*='veteran'], select[name*='disability']").all()
        for select in eeo_selects[:5]:  # Limit to first 5
            try:
                if select.is_visible(timeout=500):
                    # Try to select "Prefer not to answer" or similar
                    options = ["Prefer not to answer", "Decline to answer", "I do not wish to answer", "Choose not to answer"]
                    for option_text in options:
                        try:
                            select.select_option(label=option_text)
                            handled = True
                            human_delay(300, 600)
                            break
                        except:
                            continue
            except:
                continue
        
        # Find radio buttons for decline options
        decline_radios = page.locator(
            "input[type='radio'][value*='decline'], "
            "input[type='radio'][value*='prefer'], "
            "input[type='radio'][value*='no']"
        ).all()
        for radio in decline_radios[:5]:
            try:
                if radio.is_visible(timeout=500):
                    radio.click()
                    handled = True
                    human_delay(300, 600)
                    break
            except:
                continue
        
        # Find decline/prefer not buttons
        decline_buttons = page.locator(
            "button:has-text('Decline'), button:has-text('Prefer not'), "
            "a:has-text('Decline'), label:has-text('Decline')"
        ).all()
        for btn in decline_buttons[:3]:
            try:
                if btn.is_visible(timeout=500):
                    btn.click()
                    handled = True
                    human_delay(300, 600)
            except:
                continue
                
    except Exception as e:
        pass
    
    return handled


def navigate_multi_step_form(page: Page, max_steps: int = 5):
    """
    Navigate through multi-step forms by clicking Next/Continue buttons.
    Checks if buttons contain submit keywords.
    
    Returns:
        (next_clicked, submit_clicked) tuple
    """
    next_clicked = False
    submit_clicked = False
    
    for attempt in range(max_steps):
        try:
            # Check if submit button is already visible
            all_btns = page.locator("button").all()
            submit_visible = False
            for btn in all_btns[:20]:
                if btn.is_visible(timeout=500):
                    btn_text = (btn.text_content() or "").lower()
                    if "send" in btn_text or "submit" in btn_text:
                        submit_visible = True
                        break
            
            if submit_visible:
                break
            
            # Find Next/Continue buttons
            next_buttons = page.locator(
                "button:has-text('Next'), button:has-text('Continue'), "
                "button:has-text('Next →'), a:has-text('Next'), "
                "button[aria-label*='Next'], button[class*='next']"
            ).all()
            
            # Filter out submit buttons
            filtered_next = []
            for btn in next_buttons:
                try:
                    btn_text = (btn.text_content() or "").lower()
                    if "send" not in btn_text and "submit" not in btn_text:
                        filtered_next.append(btn)
                except:
                    filtered_next.append(btn)
            
            clicked = False
            for next_btn in filtered_next:
                try:
                    if next_btn.is_visible(timeout=1000):
                        is_disabled = next_btn.evaluate("el => el.disabled")
                        if not is_disabled:
                            # Get full text including nested elements
                            full_text = next_btn.evaluate("""
                                el => {
                                    const clone = el.cloneNode(true);
                                    const spans = clone.querySelectorAll('span, div');
                                    spans.forEach(s => s.style.display = 'inline');
                                    return clone.textContent || el.textContent || '';
                                }
                            """)
                            full_text_lower = full_text.lower()
                            
                            # Check if this is actually a submit button
                            if "send" in full_text_lower or "submit" in full_text_lower:
                                next_btn.scroll_into_view_if_needed()
                                human_delay(500, 1000)
                                next_btn.click()
                                submit_clicked = True
                                human_delay(3000, 5000)
                                clicked = True
                                break
                            else:
                                next_btn.scroll_into_view_if_needed()
                                human_delay(500, 1000)
                                next_btn.click()
                                next_clicked = True
                                clicked = True
                                human_delay(3000, 5000)
                                break
                except:
                    continue
            
            if submit_clicked or not clicked:
                break
                
        except:
            break
    
    return (next_clicked, submit_clicked)


def find_and_click_submit_button(page: Page) -> bool:
    """
    Comprehensive submit button detection and clicking.
    
    Returns:
        True if submit button was clicked
    """
    submit_clicked = False
    
    # Scroll to bottom
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    human_delay(2000, 3000)
    page.wait_for_timeout(2000)
    
    # Submit button selectors
    submit_selectors = [
        "button[type='submit']",
        "input[type='submit']",
        "button:has-text('Submit')",
        "button:has-text('Send Application')",
        "button:has-text('Submit Application')",
        "button:has-text('Apply')",
        "a:has-text('Submit')",
        "a:has-text('Send Application')",
        "button.primary",
        "button.btn-primary",
        "button[aria-label*='Submit']",
        "button[aria-label*='Send']",
        "#submit",
        ".submit-button"
    ]
    
    submit_texts = ["Send Application", "Submit Application", "Submit", "Apply", "Send"]
    
    # Method 1: Try selectors
    for selector in submit_selectors:
        try:
            buttons = page.locator(selector).all()
            for btn in buttons:
                try:
                    if btn.is_visible(timeout=1000):
                        btn.scroll_into_view_if_needed()
                        human_delay(500, 1000)
                        
                        is_disabled = btn.evaluate("el => el.disabled || el.style.display === 'none'")
                        if not is_disabled:
                            btn_text = (btn.text_content() or "").strip().lower()
                            if any(text.lower() in btn_text for text in submit_texts) or selector.startswith("button[type='submit']"):
                                btn.click()
                                submit_clicked = True
                                human_delay(3000, 5000)
                                
                                # Check for success
                                try:
                                    page.wait_for_timeout(2000)
                                    current_url = page.url
                                    page_text = (page.locator("body").text_content() or "").lower()
                                    
                                    if any(ind in current_url.lower() for ind in ["thank", "success", "confirmation"]):
                                        submit_clicked = True
                                    elif any(ind in page_text for ind in ["thank you", "application received", "successfully submitted"]):
                                        submit_clicked = True
                                except:
                                    pass
                                
                                break
                except:
                    continue
            if submit_clicked:
                break
        except:
            continue
    
    # Method 2: Try all buttons
    if not submit_clicked:
        try:
            all_buttons = page.locator("button, input[type='submit']").all()
            for btn in all_buttons:
                try:
                    if btn.is_visible(timeout=500):
                        btn_text = (btn.text_content() or btn.get_attribute("value") or "").strip().lower()
                        if any(text.lower() in btn_text for text in submit_texts):
                            is_disabled = btn.evaluate("el => el.disabled || el.style.display === 'none'")
                            if not is_disabled:
                                btn.scroll_into_view_if_needed()
                                human_delay(500, 1000)
                                btn.click()
                                submit_clicked = True
                                human_delay(3000, 5000)
                                break
                except:
                    continue
        except:
            pass
    
    # Method 3: If only one button remains, click it
    if not submit_clicked:
        try:
            remaining_buttons = page.locator("button:visible").all()
            if len(remaining_buttons) == 1:
                last_button = remaining_buttons[0]
                is_disabled = last_button.evaluate("el => el.disabled")
                if not is_disabled:
                    last_button.scroll_into_view_if_needed()
                    human_delay(500, 1000)
                    last_button.click()
                    submit_clicked = True
                    human_delay(3000, 5000)
        except:
            pass
    
    # Method 4: JavaScript fallback
    if not submit_clicked:
        try:
            submit_found = page.evaluate("""
                () => {
                    const buttons = Array.from(document.querySelectorAll('button, input[type="submit"]'));
                    for (let btn of buttons) {
                        const text = (btn.textContent || btn.value || '').toLowerCase();
                        if ((text.includes('send') || text.includes('submit')) && 
                            !btn.disabled && btn.offsetParent !== null) {
                            btn.scrollIntoView({behavior: 'smooth', block: 'center'});
                            setTimeout(() => btn.click(), 500);
                            return true;
                        }
                    }
                    return false;
                }
            """)
            if submit_found:
                submit_clicked = True
                human_delay(3000, 5000)
        except:
            pass
    
    return submit_clicked

