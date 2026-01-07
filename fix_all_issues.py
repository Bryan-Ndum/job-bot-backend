"""
Comprehensive Fix Script - Fixes Database Schema and Other Issues
"""

import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

print("\n" + "="*70)
print("COMPREHENSIVE FIX SCRIPT")
print("="*70 + "\n")

# Step 1: Generate SQL to fix database schema
print("STEP 1: Database Schema Fix\n")

sql_fix = """
-- ============================================
-- Fix Missing Columns in applications Table
-- Run this in Supabase SQL Editor
-- ============================================

-- Add missing columns if they don't exist
DO $$ 
BEGIN
    -- Add user_id column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'applications' AND column_name = 'user_id'
    ) THEN
        ALTER TABLE applications ADD COLUMN user_id TEXT;
        RAISE NOTICE 'Added user_id column';
    END IF;
    
    -- Add date_applied column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'applications' AND column_name = 'date_applied'
    ) THEN
        ALTER TABLE applications ADD COLUMN date_applied TIMESTAMP DEFAULT NOW();
        RAISE NOTICE 'Added date_applied column';
    END IF;
END $$;

-- Create index on user_id if it doesn't exist
CREATE INDEX IF NOT EXISTS idx_applications_user_id ON applications(user_id);

-- Verify the fix
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'applications'
ORDER BY ordinal_position;
"""

# Save SQL to file
sql_file = "fix_database_schema.sql"
with open(sql_file, "w", encoding="utf-8") as f:
    f.write(sql_fix)

print(f"✓ SQL fix saved to: {sql_file}")
print("\nTo apply this fix:")
print("1. Go to: https://supabase.com/dashboard")
print("2. Select your project")
print("3. Go to: SQL Editor (left sidebar)")
print("4. Click: New Query")
print(f"5. Copy contents from: {sql_file}")
print("6. Click: Run (or press Ctrl+Enter)")
print()

# Step 2: Check for other issues
print("="*70)
print("STEP 2: Checking for Other Issues\n")

issues_found = []
fixes_applied = []

# Check if resume exists
print("Checking resume file...")
resume_path = os.path.abspath(os.path.join("storage", "resumes", "pdf", "resume.pdf"))
if os.path.exists(resume_path):
    print(f"✓ Resume found at: {resume_path}")
else:
    issues_found.append(f"Resume not found at: {resume_path}")
    print(f"✗ Resume not found at: {resume_path}")

# Check if storage directories exist
print("\nChecking storage directories...")
dirs_to_check = [
    "storage/resumes/pdf",
    "storage/cover_letters",
    "storage/browser_context",
    "storage/screenshots"
]

for dir_path in dirs_to_check:
    full_path = os.path.abspath(dir_path)
    if not os.path.exists(full_path):
        os.makedirs(full_path, exist_ok=True)
        fixes_applied.append(f"Created directory: {dir_path}")
        print(f"✓ Created: {dir_path}")
    else:
        print(f"✓ Exists: {dir_path}")

# Check .env file
print("\nChecking environment variables...")
from dotenv import load_dotenv
load_dotenv()

required_vars = ["SUPABASE_URL", "SUPABASE_SERVICE_KEY", "OPENAI_API_KEY"]
missing_vars = []

for var in required_vars:
    value = os.getenv(var)
    if value:
        print(f"✓ {var}: SET")
    else:
        missing_vars.append(var)
        print(f"✗ {var}: MISSING")
        issues_found.append(f"Missing environment variable: {var}")

# Check application tracker error handling
print("\nChecking application tracker...")
try:
    from app.services.application_tracker import has_applied_to_url
    print("✓ Application tracker module imported successfully")
except Exception as e:
    issues_found.append(f"Application tracker import error: {e}")
    print(f"✗ Application tracker import error: {e}")

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70 + "\n")

if issues_found:
    print(f"⚠️  Found {len(issues_found)} issue(s):")
    for issue in issues_found:
        print(f"   - {issue}")
else:
    print("✓ No critical issues found")

if fixes_applied:
    print(f"\n✓ Applied {len(fixes_applied)} fix(es):")
    for fix in fixes_applied:
        print(f"   - {fix}")

print("\n" + "="*70)
print("NEXT STEPS")
print("="*70 + "\n")
print("1. Run the SQL fix in Supabase SQL Editor (see file: fix_database_schema.sql)")
print("2. After running SQL, applications will be tracked properly")
print("3. The business analyst script will then track all new applications")
print("\n" + "="*70 + "\n")

