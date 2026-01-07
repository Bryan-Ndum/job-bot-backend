"""
Create Supabase Tables Directly
Uses Supabase REST API to create tables programmatically.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("ERROR: Missing Supabase credentials in .env")
    exit(1)

# Remove trailing slash if present
SUPABASE_URL = SUPABASE_URL.rstrip('/')

# Headers for Supabase REST API
headers = {
    "apikey": SUPABASE_SERVICE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    "Content-Type": "application/json"
}

# SQL statements
SQL_STATEMENTS = [
    """
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
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_networking_user_id ON networking_contacts(user_id);
    CREATE INDEX IF NOT EXISTS idx_networking_application_id ON networking_contacts(application_id);
    """,
    """
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
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_applications_user_id ON applications(user_id);
    CREATE INDEX IF NOT EXISTS idx_applications_application_id ON applications(application_id);
    CREATE INDEX IF NOT EXISTS idx_applications_callback_status ON applications(callback_status);
    """,
    """
    CREATE TABLE IF NOT EXISTS resume_data (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        dataset_name TEXT UNIQUE NOT NULL,
        content JSONB NOT NULL,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    );
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_resume_data_dataset_name ON resume_data(dataset_name);
    """
]


def execute_sql_via_rpc(sql: str) -> bool:
    """
    Execute SQL via Supabase RPC (Remote Procedure Call).
    This requires a function to be created in Supabase first.
    """
    # This approach requires a stored procedure in Supabase
    # Not ideal for one-time setup
    return False


def create_table_manually():
    """
    Since Supabase Python client doesn't support direct SQL execution,
    we'll provide the SQL that needs to be run in Supabase SQL Editor.
    """
    print("\n" + "="*70)
    print("SUPABASE DATABASE SETUP")
    print("="*70)
    print("\nThe Supabase Python client doesn't support direct SQL execution.")
    print("Please run the SQL below in Supabase SQL Editor.\n")
    print("Steps:")
    print("1. Go to: https://supabase.com/dashboard")
    print("2. Select your project")
    print("3. Go to: SQL Editor (left sidebar)")
    print("4. Click: New Query")
    print("5. Paste the SQL below")
    print("6. Click: Run (or press Ctrl+Enter)\n")
    print("="*70)
    print("\n--- COPY SQL BELOW ---\n")
    
    combined_sql = "\n".join(SQL_STATEMENTS)
    print(combined_sql)
    
    print("\n--- END SQL ---\n")
    print("="*70)
    
    # Also save to file
    with open("database_setup.sql", "w", encoding="utf-8") as f:
        f.write("-- Supabase Database Setup SQL\n")
        f.write("-- Run this in Supabase SQL Editor\n\n")
        f.write(combined_sql)
    
    print("\nSQL also saved to: database_setup.sql")
    print("\nAfter running the SQL, verify tables exist by running:")
    print("  python Scripts/setup_database.py\n")


if __name__ == "__main__":
    print(f"\nConnecting to Supabase: {SUPABASE_URL}\n")
    create_table_manually()






