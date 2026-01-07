# Captcha Bypass Setup Guide

## Quick Start

### 1. Choose a Captcha Solving Service

**2Captcha (Recommended)**
- Website: https://2captcha.com
- Price: ~$2.99 per 1000 captchas
- Sign up and add funds
- Get your API key from the dashboard

**Anti-Captcha (Alternative)**
- Website: https://anti-captcha.com  
- Similar pricing
- Sign up and get API key

### 2. Set Environment Variable

Add to your `.env` file:

```bash
# For 2Captcha
CAPTCHA_2CAPTCHA_API_KEY=your_api_key_here

# OR for Anti-Captcha
CAPTCHA_ANTICAPTCHA_API_KEY=your_api_key_here
```

### 3. Usage

The captcha handler is **automatically integrated** into the auto-apply system. It will:

1. ✅ Detect captchas when they appear
2. ✅ Solve them using your configured service
3. ✅ Inject the solution token
4. ✅ Continue with the application

**No additional code needed!** Just set the API key and it works automatically.

## Manual Usage (Optional)

If you want to handle captchas manually:

```python
from app.services.captcha_handler import CaptchaHandler
from playwright.sync_api import sync_playwright

handler = CaptchaHandler(service="2captcha", api_key="your_key")

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://example.com")
    
    result = handler.solve_and_inject(page)
    if result["success"]:
        print("Captcha solved!")
```

## Cost Estimate

- **Per captcha**: ~$0.003
- **100 applications with captchas**: ~$0.30
- **1000 applications**: ~$3.00

Most applications don't have captchas, so actual costs are usually lower.

## Supported Captcha Types

| Type | Status | Notes |
|------|--------|-------|
| reCAPTCHA v2 | ✅ Fully Supported | Most common |
| hCaptcha | 🚧 Detection Ready | Solving in progress |
| Cloudflare Turnstile | 🚧 Detection Ready | Solving in progress |
| Image Captchas | 🚧 Detection Ready | Solving in progress |

## Troubleshooting

### "No API key provided"
- Make sure `CAPTCHA_2CAPTCHA_API_KEY` is set in `.env`
- Or pass `captcha_api_key` parameter to functions

### "Captcha not solved in time"
- Check your service balance
- Some captchas take 30-60 seconds to solve
- This is normal

### "Failed to inject token"
- Rare - may need browser update
- Check browser console for errors

## Best Practices

1. **Monitor Costs**: Check your service dashboard regularly
2. **Start Small**: Test with a few applications first
3. **Balance Check**: Ensure adequate balance in your account
4. **Legal Use**: Only use for legitimate automation purposes

## Disabling Captcha Solving

To disable captcha solving, simply don't set the API key. The system will:
- Still detect captchas
- Log warnings when captchas are found
- Continue (may fail if captcha is required)
- No charges incurred






