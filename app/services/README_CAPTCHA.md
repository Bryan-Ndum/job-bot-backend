# Captcha Bypass Integration

## Overview
The system includes captcha detection and solving capabilities using third-party services. This allows the automation to handle captcha challenges when they appear during job applications.

## Supported Services

### 1. 2Captcha
- **Website**: https://2captcha.com
- **Pricing**: ~$2.99 per 1000 captchas
- **Support**: reCAPTCHA v2, hCaptcha, image captchas
- **Setup**: 
  1. Sign up at 2captcha.com
  2. Add funds to your account
  3. Get your API key
  4. Set environment variable: `CAPTCHA_2CAPTCHA_API_KEY=your_api_key`

### 2. Anti-Captcha
- **Website**: https://anti-captcha.com
- **Pricing**: Similar pricing to 2Captcha
- **Support**: reCAPTCHA v2/v3, hCaptcha, FunCaptcha
- **Setup**:
  1. Sign up at anti-captcha.com
  2. Add funds
  3. Get your API key
  4. Set environment variable: `CAPTCHA_ANTICAPTCHA_API_KEY=your_api_key`

## Supported Captcha Types

- ✅ **reCAPTCHA v2** - Fully supported
- 🚧 **hCaptcha** - Detection ready, solving in progress
- 🚧 **Cloudflare Turnstile** - Detection ready
- 🚧 **Image Captchas** - Detection ready

## Usage

### Automatic Detection and Solving

The captcha handler is automatically integrated into the Playwright apply engine. It will:

1. Detect captchas on the page
2. Solve them using the configured service
3. Inject the solution token
4. Continue with the application

```python
from app.services.playwright_apply import apply_with_playwright

result = apply_with_playwright(
    url="https://linkedin.com/jobs/view/123",
    resume_path="resume.pdf",
    captcha_service="2captcha",
    captcha_api_key="your_api_key"  # Optional if env var is set
)
```

### Manual Captcha Handling

You can also handle captchas manually:

```python
from app.services.captcha_handler import CaptchaHandler
from playwright.sync_api import sync_playwright

handler = CaptchaHandler(service="2captcha", api_key="your_key")

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://example.com/job-apply")
    
    # Detect and solve
    result = handler.solve_and_inject(page)
    
    if result["success"]:
        print(f"Captcha solved: {result['type']}")
    else:
        print(f"Error: {result['error']}")
```

## Environment Variables

Add to your `.env` file:

```bash
# 2Captcha
CAPTCHA_2CAPTCHA_API_KEY=your_2captcha_api_key

# Anti-Captcha (alternative)
CAPTCHA_ANTICAPTCHA_API_KEY=your_anticaptcha_api_key
```

## Cost Considerations

- Captcha solving services charge per captcha solved
- Typical cost: $0.002-0.003 per captcha
- For 1000 applications with captchas: ~$2-3
- Consider setting a budget limit in your service account

## Fallback Behavior

If captcha solving fails or is not configured:
- The system will log a warning
- Application will continue (may fail if captcha is required)
- Error will be returned in the result

## Best Practices

1. **Monitor Costs**: Keep track of captcha solving costs
2. **Use Selectively**: Only enable for sites that require captchas
3. **Handle Failures**: Check result status and handle failures gracefully
4. **Rate Limiting**: Some services have rate limits - respect them
5. **Compliance**: Ensure your use case complies with the captcha service's terms of service

## Troubleshooting

### "No API key provided"
- Set the environment variable or pass `captcha_api_key` parameter
- Verify the key is correct

### "Captcha not solved in time"
- Increase timeout in `CaptchaHandler` configuration
- Check service status/balance
- Try a different service

### "Failed to inject token"
- The page structure may have changed
- Check browser console for errors
- May need to update injection logic

## Legal and Ethical Considerations

- Only use captcha solving for legitimate automation purposes
- Respect website terms of service
- Use captcha solving services that comply with legal requirements
- Don't abuse the system or websites






