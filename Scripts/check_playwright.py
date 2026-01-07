"""
Check Playwright and Chromium Installation
"""

import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print("\n" + "="*70)
print("Playwright Installation Check")
print("="*70 + "\n")

# Check 1: Playwright package
print("1. Checking Playwright package...")
try:
    import playwright
    try:
        version = playwright.__version__
        print(f"   ✓ Playwright package installed (version: {version})")
    except AttributeError:
        print("   ✓ Playwright package installed")
except ImportError:
    print("   ✗ Playwright package NOT installed")
    print("   → Install with: pip install playwright")
    sys.exit(1)

# Check 2: Playwright API
print("\n2. Checking Playwright API...")
try:
    from playwright.sync_api import sync_playwright, Page, Browser
    print("   ✓ Playwright API imported successfully")
except ImportError as e:
    print(f"   ✗ Playwright API import failed: {e}")
    sys.exit(1)

# Check 3: Chromium browser
print("\n3. Checking Chromium browser...")
try:
    playwright_obj = sync_playwright().start()
    browser = playwright_obj.chromium.launch(headless=True)
    print("   ✓ Chromium browser installed and working")
    browser.close()
    playwright_obj.stop()
except Exception as e:
    error_msg = str(e)
    if "Executable doesn't exist" in error_msg or "BrowserType.launch" in error_msg:
        print("   ✗ Chromium browser NOT installed")
        print("   → Install with: playwright install chromium")
        print(f"   Error: {error_msg}")
    else:
        print(f"   ✗ Chromium test failed: {error_msg}")
    sys.exit(1)

# Check 4: Other browsers (optional)
print("\n4. Checking other browsers (optional)...")
try:
    playwright_obj = sync_playwright().start()
    
    browsers = {
        "firefox": playwright_obj.firefox,
        "webkit": playwright_obj.webkit
    }
    
    for name, browser_type in browsers.items():
        try:
            browser = browser_type.launch(headless=True)
            browser.close()
            print(f"   ✓ {name.capitalize()} installed")
        except:
            print(f"   - {name.capitalize()} not installed (optional)")
    
    playwright_obj.stop()
except Exception as e:
    print(f"   (Skipping optional browser check: {e})")

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print("✓ Playwright: INSTALLED AND READY")
print("✓ Chromium: INSTALLED AND READY")
print("\nYou can use auto-apply features now!\n")

