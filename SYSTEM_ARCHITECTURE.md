# Automated Job Application System Architecture

## Overview
High-volume automated job application system optimized for interview callbacks, not raw application count. The system applies to many jobs at scale while maximizing recruiter response probability.

## System Components

### 1. Job Intake and Parsing (`app/services/job_intake.py`)
- **Inputs**: Job URLs, pasted descriptions, saved job lists
- **Output**: Structured job data with company, role, ATS type, skills, location, etc.
- **Features**:
  - AI-powered extraction using GPT-4o-mini
  - ATS detection
  - Batch processing support

### 2. Job Fit Probability Scoring (`app/services/job_fit_scorer.py`)
- **Scoring Range**: 0-100 based on callback likelihood
- **Scoring Factors**:
  - Required skill overlap (30 points)
  - Tech stack match (25 points)
  - Preferred skills (10 points)
  - Seniority alignment (10 points)
  - Location compatibility (10 points)
  - Keyword alignment (10 points)
  - Domain familiarity (5 points)
- **Decision Rules**:
  - Score >= 80 → Priority apply
  - Score 65-79 → Apply at scale
  - Score < 65 → Skip

### 3. Resume and Cover Letter Optimization (`app/services/resume_optimizer.py`)
- **Resume Rules**:
  - One-page, recruiter-readable format
  - Metrics in first bullets
  - Skills reordered to match job description
  - No visual clutter
- **Cover Letter Rules**:
  - 200-250 words maximum
  - Company/product reference paragraph
  - Role alignment paragraph
  - Optional closing paragraph
- **Adaptation Levels**:
  - Deep customization for fit_score >= 80
  - Light customization for fit_score 65-79

### 4. Auto-Apply Execution Engine (`app/services/playwright_apply.py`)
- **Tooling**: Playwright with headful browser mode
- **Features**:
  - Human-like typing and delays
  - ATS platform detection
  - Auto-fill standard fields
  - Resume and cover letter upload
  - Basic screening question answers
  - **Captcha detection and solving** (integrated)
- **Principle**: Completes ~80% of application, user completes remaining 20%

### 4.1. Captcha Handler (`app/services/captcha_handler.py`)
- **Services Supported**: 2Captcha, Anti-Captcha
- **Captcha Types**: reCAPTCHA v2 (fully supported), hCaptcha, Cloudflare Turnstile (detection ready)
- **Features**:
  - Automatic captcha detection
  - Integration with third-party solving services
  - Token injection and verification
  - Cost-aware (only solves when necessary)
- **Setup**: Set `CAPTCHA_2CAPTCHA_API_KEY` environment variable

### 5. Callback Tracking and Optimization (`app/services/callback_tracker.py`)
- **Tracks**:
  - Application details
  - Fit scores
  - Resume/cover letter versions
  - Callback status (pending, callback, interview, rejected)
- **Optimization**:
  - Identifies high-performing resume versions
  - Tracks callback rates per version
  - Recommends optimal resume version
  - Analyzes patterns for improvement

### 6. Networking Signal Generation (`app/services/networking_signal.py`)
- **Features**:
  - Generates personalized LinkedIn follow-up messages
  - Identifies recruiter/hiring manager (placeholder)
  - Stores contact information
  - Batch message generation

### 7. Main Orchestrator (`app/services/job_application_orchestrator.py`)
- **Coordinates all components**:
  1. Parse job data
  2. Score job fit
  3. Generate optimized resume/cover letter
  4. Auto-apply (if enabled)
  5. Track application
  6. Generate networking signal
- **Supports**:
  - Single job processing
  - Batch job processing
  - Saved job list processing

## API Endpoints

### `/api/jobs/apply` (POST)
Apply to a single job URL.

**Request Body**:
```json
{
  "url": "https://linkedin.com/jobs/view/123",
  "job_description": "Optional description",
  "user_id": "user123",
  "user_info": {
    "first_name": "Bryan",
    "last_name": "Ndum",
    "email": "email@example.com"
  },
  "auto_apply": false
}
```

### `/api/jobs/apply/batch` (POST)
Apply to multiple jobs in batch.

**Request Body**:
```json
{
  "jobs": [
    {"url": "...", "description": "..."},
    {"url": "...", "description": "..."}
  ],
  "user_id": "user123",
  "auto_apply": false,
  "min_score": 65
}
```

## Usage Example

```python
from app.services.job_application_orchestrator import apply_to_job

result = apply_to_job(
    url="https://linkedin.com/jobs/view/123",
    job_description="IT Support Analyst role...",
    user_id="user123",
    user_info={"email": "bryan@example.com"},
    auto_apply=False  # Set True to actually apply
)

print(f"Fit Score: {result['fit_score']}")
print(f"Decision: {result['decision']}")
```

## Database Schema

### Applications Table
- `application_id` (primary key)
- `user_id`
- `company`
- `role`
- `fit_score`
- `resume_version`
- `cover_letter_version`
- `url`
- `date_applied`
- `callback_status` (pending, callback, interview, rejected)
- `callback_date`
- `interview_date`
- `notes`

### Networking Contacts Table
- `application_id`
- `user_id`
- `company`
- `role`
- `recruiter_name`
- `recruiter_linkedin`
- `message`
- `message_sent`
- `created_at`

## Testing

Run the test script:
```bash
python Tests/test_job_application_system.py
```

## Dependencies

- `playwright` - Browser automation
- `openai` - AI-powered job parsing and content generation
- `supabase` - Database for tracking
- `fastapi` - API framework

## Future Enhancements

1. LinkedIn API integration for recruiter identification
2. Enhanced ATS platform support
3. Advanced question answering with context
4. Automated callback status updates via email parsing
5. Resume version A/B testing
6. Machine learning model for fit score prediction

