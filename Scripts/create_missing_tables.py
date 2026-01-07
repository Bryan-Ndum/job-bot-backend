"""
Create Missing Supabase Tables
Checks which tables exist and provides SQL to create missing ones.
"""

import os
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("ERROR: Missing Supabase credentials in .env")
    sys.exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

print("\n" + "="*70)
print("Checking Supabase Tables...")
print("="*70 + "\n")

# Required tables
REQUIRED_TABLES = {
    "applications": {
        "exists": False,
        "sql": """
CREATE TABLE IF NOT EXISTS applications (
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

CREATE INDEX IF NOT EXISTS idx_applications_user_id ON applications(user_id);
CREATE INDEX IF NOT EXISTS idx_applications_application_id ON applications(application_id);
CREATE INDEX IF NOT EXISTS idx_applications_callback_status ON applications(callback_status);
"""
    },
    "networking_contacts": {
        "exists": False,
        "sql": """
CREATE TABLE IF NOT EXISTS networking_contacts (
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

CREATE INDEX IF NOT EXISTS idx_networking_user_id ON networking_contacts(user_id);
CREATE INDEX IF NOT EXISTS idx_networking_application_id ON networking_contacts(application_id);
"""
    },
    "resume_data": {
        "exists": False,
        "sql": """
CREATE TABLE IF NOT EXISTS resume_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dataset_name TEXT UNIQUE NOT NULL,
    content JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_resume_data_dataset_name ON resume_data(dataset_name);
"""
    }
}

# Check which tables exist
for table_name in REQUIRED_TABLES.keys():
    try:
        # Try to query the table (limit 0 to just check existence)
        result = supabase.table(table_name).select("*").limit(0).execute()
        REQUIRED_TABLES[table_name]["exists"] = True
        print(f"✓ {table_name}: EXISTS")
    except Exception as e:
        error_msg = str(e)
        if "does not exist" in error_msg.lower() or "PGRST205" in error_msg or "relation" in error_msg.lower():
            REQUIRED_TABLES[table_name]["exists"] = False
            print(f"✗ {table_name}: MISSING")
        else:
            # Other error - might exist but have permission issue
            print(f"? {table_name}: CHECK FAILED - {error_msg[:50]}")

# Find missing tables
missing_tables = {name: data for name, data in REQUIRED_TABLES.items() if not data["exists"]}

if not missing_tables:
    print("\n" + "="*70)
    print("SUCCESS: All required tables exist!")
    print("="*70 + "\n")
    sys.exit(0)

# Generate SQL for missing tables
print("\n" + "="*70)
print(f"Found {len(missing_tables)} missing table(s)")
print("="*70 + "\n")

print("To create missing tables, run this SQL in Supabase SQL Editor:\n")
print("1. Go to: https://supabase.com/dashboard")
print("2. Select your project")
print("3. Click: SQL Editor (left sidebar)")
print("4. Click: New Query")
print("5. Copy and paste the SQL below")
print("6. Click: Run (or Ctrl+Enter)\n")
print("-"*70)
print("\n-- SQL TO RUN:\n")

sql_to_run = []
for table_name, table_data in missing_tables.items():
    sql_to_run.append(f"-- Create {table_name} table")
    sql_to_run.append(table_data["sql"])

combined_sql = "\n".join(sql_to_run)
print(combined_sql)
print("\n" + "-"*70)

# Save to file
output_file = "create_missing_tables.sql"
with open(output_file, "w", encoding="utf-8") as f:
    f.write("-- Missing Tables SQL\n")
    f.write("-- Run this in Supabase SQL Editor\n\n")
    f.write(combined_sql)

print(f"\nSQL saved to: {output_file}")
print("\nAfter running the SQL, run this script again to verify.\n")






