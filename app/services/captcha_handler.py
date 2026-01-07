"""
Captcha Bypass Handler Module
Handles captcha detection and solving using third-party services.
"""

import time
import requests
from typing import Optional, Dict
from playwright.sync_api import Page


class CaptchaHandler:
    """
    Handles captcha detection and solving.
    Supports 2Captcha, Anti-Captcha, and other services.
    """
    
    def __init__(self, service: str = "2captcha", api_key: Optional[str] = None):
        """
        Initialize captcha handler.
        
        Args:
            service: Service provider ('2captcha', 'anticaptcha', 'capmonster')
            api_key: API key for the service
        """
        self.service = service.lower()
        self.api_key = api_key or self._get_api_key_from_env()
        
        # Service endpoints
        self.service_config = {
            "2captcha": {
                "submit_url": "http://2captcha.com/in.php",
                "result_url": "http://2captcha.com/res.php",
                "timeout": 120  # seconds
            },
            "anticaptcha": {
                "submit_url": "https://api.anti-captcha.com/createTask",
                "result_url": "https://api.anti-captcha.com/getTaskResult",
                "timeout": 120
            }
        }
    
    def _get_api_key_from_env(self) -> Optional[str]:
        """Get API key from environment variables."""
        import os
        key_map = {
            "2captcha": "CAPTCHA_2CAPTCHA_API_KEY",
            "anticaptcha": "CAPTCHA_ANTICAPTCHA_API_KEY"
        }
        env_key = key_map.get(self.service)
        return os.getenv(env_key) if env_key else None
    
    def detect_captcha(self, page: Page) -> Dict:
        """
        Detect if a captcha is present on the page.
        
        Returns:
            {
                "detected": bool,
                "type": str,  # "recaptcha", "hcaptcha", "cloudflare", "image"
                "element": Optional[ElementHandle]
            }
        """
        try:
            # Check for reCAPTCHA
            recaptcha_frame = page.locator('iframe[src*="recaptcha"]').first
            if recaptcha_frame.count() > 0:
                return {
                    "detected": True,
                    "type": "recaptcha",
                    "element": recaptcha_frame
                }
            
            # Check for hCaptcha
            hcaptcha_frame = page.locator('iframe[src*="hcaptcha"]').first
            if hcaptcha_frame.count() > 0:
                return {
                    "detected": True,
                    "type": "hcaptcha",
                    "element": hcaptcha_frame
                }
            
            # Check for Cloudflare Turnstile
            turnstile_frame = page.locator('iframe[src*="challenges.cloudflare.com"]').first
            if turnstile_frame.count() > 0:
                return {
                    "detected": True,
                    "type": "cloudflare",
                    "element": turnstile_frame
                }
            
            # Check for image captcha
            captcha_image = page.locator('img[alt*="captcha"], img[src*="captcha"]').first
            if captcha_image.count() > 0:
                return {
                    "detected": True,
                    "type": "image",
                    "element": captcha_image
                }
            
            # Check for text indicating captcha
            captcha_text = page.locator('text=/captcha|verification|verify/i').first
            if captcha_text.count() > 0:
                return {
                    "detected": True,
                    "type": "unknown",
                    "element": None
                }
            
            return {"detected": False, "type": None, "element": None}
            
        except Exception as e:
            return {"detected": False, "type": None, "element": None, "error": str(e)}
    
    def solve_recaptcha_v2(self, page: Page, site_key: Optional[str] = None) -> Dict:
        """
        Solve reCAPTCHA v2 using 2Captcha service.
        
        Args:
            page: Playwright page object
            site_key: reCAPTCHA site key (extracted automatically if not provided)
        
        Returns:
            {"success": bool, "token": Optional[str], "error": Optional[str]}
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "No API key provided for captcha solving service"
            }
        
        try:
            # Extract site key if not provided
            if not site_key:
                site_key = self._extract_recaptcha_site_key(page)
            
            if not site_key:
                return {
                    "success": False,
                    "error": "Could not extract reCAPTCHA site key"
                }
            
            # Get page URL for 2captcha
            page_url = page.url
            
            if self.service == "2captcha":
                return self._solve_recaptcha_2captcha(page_url, site_key)
            elif self.service == "anticaptcha":
                return self._solve_recaptcha_anticaptcha(page_url, site_key)
            else:
                return {
                    "success": False,
                    "error": f"Service {self.service} not implemented for reCAPTCHA"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _extract_recaptcha_site_key(self, page: Page) -> Optional[str]:
        """Extract reCAPTCHA site key from page."""
        try:
            # Try to find site key in iframe src
            iframe = page.locator('iframe[src*="recaptcha"]').first
            if iframe.count() > 0:
                src = iframe.get_attribute("src")
                if src and "k=" in src:
                    site_key = src.split("k=")[1].split("&")[0]
                    return site_key
            
            # Try to find in page content
            content = page.content()
            import re
            matches = re.findall(r'data-sitekey=["\']([^"\']+)["\']', content)
            if matches:
                return matches[0]
            
            # Try to find in script tags
            site_key_pattern = re.compile(r'sitekey["\']?\s*[:=]\s*["\']([^"\']+)["\']')
            matches = site_key_pattern.findall(content)
            if matches:
                return matches[0]
            
            return None
            
        except Exception:
            return None
    
    def _solve_recaptcha_2captcha(self, page_url: str, site_key: str) -> Dict:
        """Solve reCAPTCHA using 2Captcha service."""
        try:
            config = self.service_config["2captcha"]
            
            # Submit captcha
            submit_params = {
                "key": self.api_key,
                "method": "userrecaptcha",
                "googlekey": site_key,
                "pageurl": page_url,
                "json": 1
            }
            
            response = requests.post(config["submit_url"], data=submit_params, timeout=30)
            result = response.json()
            
            if result.get("status") != 1:
                return {
                    "success": False,
                    "error": f"2Captcha submission failed: {result.get('request', 'Unknown error')}"
                }
            
            captcha_id = result.get("request")
            
            # Poll for result
            max_wait = config["timeout"]
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                time.sleep(5)  # Wait 5 seconds between checks
                
                result_params = {
                    "key": self.api_key,
                    "action": "get",
                    "id": captcha_id,
                    "json": 1
                }
                
                result_response = requests.get(config["result_url"], params=result_params, timeout=30)
                result_data = result_response.json()
                
                if result_data.get("status") == 1:
                    token = result_data.get("request")
                    return {
                        "success": True,
                        "token": token,
                        "captcha_id": captcha_id
                    }
                elif result_data.get("request") == "CAPCHA_NOT_READY":
                    continue  # Keep waiting
                else:
                    return {
                        "success": False,
                        "error": f"2Captcha solving failed: {result_data.get('request', 'Unknown error')}"
                    }
            
            return {
                "success": False,
                "error": "2Captcha timeout - captcha not solved in time"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _solve_recaptcha_anticaptcha(self, page_url: str, site_key: str) -> Dict:
        """Solve reCAPTCHA using Anti-Captcha service."""
        try:
            config = self.service_config["anticaptcha"]
            
            # Create task
            task_data = {
                "clientKey": self.api_key,
                "task": {
                    "type": "NoCaptchaTaskProxyless",
                    "websiteURL": page_url,
                    "websiteKey": site_key
                }
            }
            
            response = requests.post(config["submit_url"], json=task_data, timeout=30)
            result = response.json()
            
            if result.get("errorId") != 0:
                return {
                    "success": False,
                    "error": f"Anti-Captcha task creation failed: {result.get('errorDescription', 'Unknown error')}"
                }
            
            task_id = result.get("taskId")
            
            # Poll for result
            max_wait = config["timeout"]
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                time.sleep(5)
                
                result_data = {
                    "clientKey": self.api_key,
                    "taskId": task_id
                }
                
                result_response = requests.post(config["result_url"], json=result_data, timeout=30)
                result_json = result_response.json()
                
                if result_json.get("status") == "ready":
                    token = result_json.get("solution", {}).get("gRecaptchaResponse")
                    return {
                        "success": True,
                        "token": token,
                        "task_id": task_id
                    }
                elif result_json.get("status") == "processing":
                    continue
                else:
                    error = result_json.get("errorDescription", "Unknown error")
                    return {
                        "success": False,
                        "error": f"Anti-Captcha solving failed: {error}"
                    }
            
            return {
                "success": False,
                "error": "Anti-Captcha timeout - captcha not solved in time"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def inject_recaptcha_token(self, page: Page, token: str) -> bool:
        """
        Inject the solved captcha token into the page.
        
        Args:
            page: Playwright page object
            token: Solved captcha token
        
        Returns:
            bool: Success status
        """
        try:
            # Inject token using JavaScript
            page.evaluate(f"""
                (function() {{
                    // For reCAPTCHA v2
                    var textarea = document.querySelector('textarea[name="g-recaptcha-response"]');
                    if (textarea) {{
                        textarea.innerHTML = '{token}';
                        textarea.style.display = 'block';
                    }}
                    
                    // Also try setting it directly
                    window.grecaptcha = window.grecaptcha || {{}};
                    if (window.grecaptcha.getResponse) {{
                        var callback = window.grecaptcha.getResponse;
                    }}
                    
                    // Trigger callback if exists
                    if (typeof ___grecaptcha_cfg !== 'undefined') {{
                        var widgets = Object.keys(___grecaptcha_cfg.widgets || {{}});
                        if (widgets.length > 0) {{
                            var widgetId = widgets[0];
                            if (window.grecaptcha && window.grecaptcha.getResponse) {{
                                try {{
                                    window.grecaptcha.execute(widgetId);
                                }} catch(e) {{
                                    console.log('Recaptcha execution:', e);
                                }}
                            }}
                        }}
                    }}
                    
                    // Set token in all possible locations
                    var elements = document.querySelectorAll('[name*="recaptcha"], [id*="recaptcha"]');
                    elements.forEach(function(el) {{
                        if (el.tagName === 'TEXTAREA') {{
                            el.value = '{token}';
                            el.innerHTML = '{token}';
                        }}
                    }});
                }})();
            """)
            
            # Wait a bit for any callbacks
            time.sleep(2)
            
            return True
            
        except Exception as e:
            print(f"Error injecting token: {e}")
            return False
    
    def solve_and_inject(self, page: Page) -> Dict:
        """
        Detect, solve, and inject captcha token automatically.
        
        Returns:
            {"success": bool, "type": str, "error": Optional[str]}
        """
        try:
            # Detect captcha
            detection = self.detect_captcha(page)
            
            if not detection.get("detected"):
                return {
                    "success": True,
                    "message": "No captcha detected",
                    "type": None
                }
            
            captcha_type = detection.get("type")
            
            if captcha_type == "recaptcha":
                # Solve reCAPTCHA
                solution = self.solve_recaptcha_v2(page)
                
                if not solution.get("success"):
                    return {
                        "success": False,
                        "type": "recaptcha",
                        "error": solution.get("error")
                    }
                
                # Inject token
                token = solution.get("token")
                injected = self.inject_recaptcha_token(page, token)
                
                if not injected:
                    return {
                        "success": False,
                        "type": "recaptcha",
                        "error": "Failed to inject token"
                    }
                
                return {
                    "success": True,
                    "type": "recaptcha",
                    "token": token
                }
            
            elif captcha_type == "hcaptcha":
                # hCaptcha solving would go here (similar to reCAPTCHA)
                return {
                    "success": False,
                    "type": "hcaptcha",
                    "error": "hCaptcha solving not yet implemented"
                }
            
            else:
                return {
                    "success": False,
                    "type": captcha_type,
                    "error": f"Captcha type '{captcha_type}' solving not implemented"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


def handle_captcha_if_present(page: Page, api_key: Optional[str] = None, service: str = "2captcha") -> Dict:
    """
    Convenience function to handle captcha if present on page.
    
    Args:
        page: Playwright page object
        api_key: API key for captcha solving service
        service: Service provider name
    
    Returns:
        {"success": bool, "handled": bool, "error": Optional[str]}
    """
    handler = CaptchaHandler(service=service, api_key=api_key)
    result = handler.solve_and_inject(page)
    
    return {
        "success": result.get("success", False),
        "handled": result.get("type") is not None,
        "type": result.get("type"),
        "error": result.get("error")
    }






