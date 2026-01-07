# Complete Setup Guide - Required API Keys & Configuration

## 📋 Overview

This document lists **ALL** API keys, credentials, and configuration needed for the job application system to operate.

---

## 🔴 REQUIRED - Core API Keys

These are **essential** and the system will not work without them.

### 1. OpenAI API Key
**Purpose**: AI-powered job parsing, resume generation, cover letter generation, question answering

**Where to get it**:
1. Go to https://platform.openai.com
2. Sign up or log in
3. Navigate to API Keys: https://platform.openai.com/api-keys
4. Click "Create new secret key"
5. Copy the key (you won't see it again!)

**Cost**: Pay-per-use (~$0.01-0.03 per resume generation)
**Free tier**: $5 free credit for new accounts

**Environment Variable**:
```bash
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

### 2. Supabase URL
**Purpose**: Database for storing applications, resumes, callbacks, networking contacts

**Where to get it**:
1. Go to https://supabase.com
2. Sign up or log in
3. Create a new project (or use existing)
4. Go to Project Settings → API
5. Copy the "Project URL"

**Cost**: Free tier available (500MB database, 1GB storage)

**Environment Variable**:
```bash
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
```

---

### 3. Supabase Service Key
**Purpose**: Admin access to Supabase database (bypasses Row Level Security)

**Where to get it**:
1. In Supabase project: Project Settings → API
2. Under "Project API keys"
3. Copy the "service_role" key (NOT the anon key)
4. ⚠️ **Keep this secret** - it has admin privileges

**Environment Variable**:
```bash
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh4eHh4eHh4eHh4eHh4eHh4eHgiLCJyb2xlIjoic2VydmljZV9yb2xlIiwiaWF0IjoxNjQ1OTk5OTk5LCJleHAiOjE5NjE1NzU5OTl9.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 🟡 OPTIONAL - Captcha Solving (Recommended)

These enable captcha bypass functionality. **Not required** but highly recommended if applying to jobs with captchas.

### 4. 2Captcha API Key
**Purpose**: Automatically solve captchas during job applications

**Where to get it**:
1. Go to https://2captcha.com
2. Sign up for an account
3. Add funds ($5 minimum recommended)
4. Go to Settings → API Key
5. Copy your API key

**Cost**: ~$2.99 per 1000 captchas (~$0.003 per captcha)
**Note**: Most applications don't have captchas, so costs are usually low

**Environment Variable**:
```bash
CAPTCHA_2CAPTCHA_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Alternative**: Anti-Captcha
```bash
CAPTCHA_ANTICAPTCHA_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 🟢 OPTIONAL - Configuration

### 5. Cloud Mode
**Purpose**: Enable cloud-specific features if deploying to cloud (AWS, GCP, etc.)

**Environment Variable**:
```bash
CLOUD_MODE=false  # or "true" for cloud deployment
```

---

## 📝 Complete .env File Template

Create a `.env` file in the root directory with all your keys:

```bash
# ============================================
# REQUIRED - Core API Keys
# ============================================

# OpenAI - Get from https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Supabase - Get from https://supabase.com → Project Settings → API
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh4eHh4eHh4eHh4eHh4eHh4eHgiLCJyb2xlIjoic2VydmljZV9yb2xlIiwiaWF0IjoxNjQ1OTk5OTk5LCJleHAiOjE5NjE1NzU5OTl9.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ============================================
# OPTIONAL - Captcha Solving (Recommended)
# ============================================

# 2Captcha - Get from https://2captcha.com → Settings → API Key
CAPTCHA_2CAPTCHA_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# OR use Anti-Captcha instead
# CAPTCHA_ANTICAPTCHA_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ============================================
# OPTIONAL - Configuration
# ============================================

# Set to "true" if deploying to cloud
CLOUD_MODE=false
```

---

## 🚀 Quick Setup Checklist

### Step 1: Get Required Keys (Essential)
- [ ] **OpenAI API Key** - https://platform.openai.com/api-keys
- [ ] **Supabase URL** - https://supabase.com → Project Settings → API
- [ ] **Supabase Service Key** - Same page as above (service_role key)

### Step 2: Set Up Supabase Database (Essential)
- [ ] Create Supabase project
- [ ] Create required tables (see Database Setup below)

### Step 3: Get Optional Keys (Recommended)
- [ ] **2Captcha API Key** - https://2captcha.com (add $5-10 balance)

### Step 4: Create .env File
- [ ] Copy template above
- [ ] Fill in all your keys
- [ ] Save as `.env` in project root

### Step 5: Test the System
- [ ] Run: `python Tests/test_resume_pipeline.py`
- [ ] Verify resume generation works
- [ ] Check Supabase connection

---

## 🗄️ Supabase Database Setup

You need to create these tables in Supabase:

### 1. Applications Table
```sql
CREATE TABLE applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_id TEXT UNIQUE NOT NULL,
    user_id TEXT NOT NULL,
    company TEXT,
    role TEXT,
    fit_score FLOAT,
    resume_version TEXT,
    cover_letter_version TEXT,
    url TEXT,
    date_applied TIMESTAMP DEFAULT NOW(),
    callback_status TEXT DEFAULT 'pending',
    callback_date TIMESTAMP,
    interview_date TIMESTAMP,
    rejection_date TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 2. Networking Contacts Table
```sql
CREATE TABLE networking_contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_id TEXT,
    user_id TEXT NOT NULL,
    company TEXT,
    role TEXT,
    recruiter_name TEXT,
    recruiter_linkedin TEXT,
    message TEXT,
    message_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 3. Resume Data Table (if using Supabase storage)
```sql
CREATE TABLE resume_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dataset_name TEXT UNIQUE NOT NULL,
    content JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Storage Buckets** (Create in Supabase Storage):
- `resumes` - For storing resume PDFs
- `screenshots` - For storing application screenshots

---

## 💰 Cost Estimates

### Minimum Monthly Costs (Free Tiers)
- **OpenAI**: $5 free credit → ~100-200 resume generations
- **Supabase**: Free tier → 500MB database, 1GB storage
- **2Captcha**: Pay-as-you-go → ~$0.003 per captcha

### Typical Usage Costs
- **50 applications/month**:
  - OpenAI: $2-5
  - Supabase: $0 (free tier)
  - 2Captcha: $0.15 (if 10% have captchas)
  - **Total: ~$2-5/month**

- **200 applications/month**:
  - OpenAI: $8-15
  - Supabase: $0 (free tier)
  - 2Captcha: $0.60
  - **Total: ~$8-15/month**

---

## 🔒 Security Best Practices

1. **Never commit `.env` file to Git**
   - Already in `.gitignore` ✓
   
2. **Use Service Role Key carefully**
   - Only use on backend/server
   - Never expose to frontend
   
3. **Rotate keys periodically**
   - Change API keys every 90 days
   - Revoke old keys immediately
   
4. **Monitor usage**
   - Set spending limits on OpenAI
   - Monitor Supabase usage dashboard
   - Check 2Captcha balance regularly

---

## ✅ Verification Steps

After setting up your `.env` file, verify everything works:

```bash
# 1. Test OpenAI connection
python -c "from app.core.config import settings; print('OpenAI:', '✅' if settings.OPENAI_API_KEY else '❌')"

# 2. Test Supabase connection
python -c "from app.core.supabase_client import get_supabase; sb = get_supabase(); print('Supabase: ✅')"

# 3. Test resume generation
python Tests/test_resume_pipeline.py

# 4. Test job application system (without auto-apply)
python Tests/test_job_application_system.py
```

---

## 🆘 Troubleshooting

### "Missing Supabase environment variables"
- Check `.env` file exists in project root
- Verify variable names match exactly (case-sensitive)
- Restart your terminal/IDE after creating `.env`

### "OpenAI API key invalid"
- Verify key starts with `sk-`
- Check for extra spaces
- Ensure key hasn't expired/revoked

### "Supabase connection failed"
- Verify URL includes `https://`
- Check Service Key (not anon key)
- Ensure project is active in Supabase dashboard

### "Captcha solving not working"
- Verify API key is correct
- Check account balance on 2Captcha
- Captcha solving is optional - system works without it

---

## 📞 Need Help?

- Check `SYSTEM_ARCHITECTURE.md` for system overview
- Check `app/services/CAPTCHA_SETUP.md` for captcha details
- Review error messages in terminal output






