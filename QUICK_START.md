# 🚀 Quick Start - API Keys Required

## Required API Keys (Must Have)

### 1. OpenAI API Key ⭐
- **Get it**: https://platform.openai.com/api-keys
- **Cost**: Pay-per-use (~$0.01-0.03 per resume)
- **Free**: $5 credit for new accounts
- **Variable**: `OPENAI_API_KEY`

### 2. Supabase URL ⭐
- **Get it**: https://supabase.com → Create Project → Settings → API
- **Cost**: Free tier available
- **Variable**: `SUPABASE_URL`

### 3. Supabase Service Key ⭐
- **Get it**: Same page as above → Copy "service_role" key
- **Cost**: Free (part of Supabase)
- **Variable**: `SUPABASE_SERVICE_KEY`

## Optional (Recommended)

### 4. 2Captcha API Key
- **Get it**: https://2captcha.com → Settings → API Key
- **Cost**: ~$2.99 per 1000 captchas
- **Variable**: `CAPTCHA_2CAPTCHA_API_KEY`

## Create Your .env File

Create a file named `.env` in the project root:

```bash
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxxxxxxxxx
CAPTCHA_2CAPTCHA_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Next Steps

1. ✅ Get all 3 required keys above
2. ✅ Create `.env` file with your keys
3. ✅ Set up Supabase database tables (see `SETUP_REQUIRED_KEYS.md`)
4. ✅ Test: `python Tests/test_resume_pipeline.py`

**Full detailed guide**: See `SETUP_REQUIRED_KEYS.md`






