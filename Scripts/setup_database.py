"""
Setup Supabase Database Tables
Creates all required tables for the job application system.
"""

import os
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("❌ Missing Supabase credentials in .env")
    print("Please set SUPABASE_URL and SUPABASE_SERVICE_KEY")
    sys.exit(1)

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

print("🔌 Connected to Supabase")
print(f"📍 URL: {SUPABASE_URL}\n")

# SQL statements to create tables
TABLES_SQL = {
    "applications": """
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
        
        -- Create index on user_id for faster queries
        CREATE INDEX IF NOT EXISTS idx_applications_user_id ON applications(user_id);
        CREATE INDEX IF NOT EXISTS idx_applications_application_id ON applications(application_id);
        CREATE INDEX IF NOT EXISTS idx_applications_callback_status ON applications(callback_status);
    """,
    
    "networking_contacts": """
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
        
        -- Create indexes
        CREATE INDEX IF NOT EXISTS idx_networking_user_id ON networking_contacts(user_id);
        CREATE INDEX IF NOT EXISTS idx_networking_application_id ON networking_contacts(application_id);
    """,
    
    "resume_data": """
        CREATE TABLE IF NOT EXISTS resume_data (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            dataset_name TEXT UNIQUE NOT NULL,
            content JSONB NOT NULL,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        
        -- Create index on dataset_name
        CREATE INDEX IF NOT EXISTS idx_resume_data_dataset_name ON resume_data(dataset_name);
    """
}

# Storage buckets configuration
STORAGE_BUCKETS = [
    {
        "name": "resumes",
        "public": False,
        "description": "Storage for resume PDFs"
    },
    {
        "name": "screenshots",
        "public": False,
        "description": "Storage for application screenshots"
    }
]


def execute_sql(sql: str, table_name: str) -> bool:
    """
    Execute SQL statement using Supabase.
    Note: Supabase Python client doesn't directly execute raw SQL.
    We'll use RPC or provide instructions.
    """
    try:
        # For Supabase, we need to use the REST API or SQL editor
        # Since Python client doesn't support raw SQL execution,
        # we'll create a helper that prints the SQL for manual execution
        # OR we can use the management API if available
        
        print(f"📝 SQL for {table_name}:")
        print("-" * 60)
        print(sql)
        print("-" * 60)
        return True
    except Exception as e:
        print(f"❌ Error with {table_name}: {e}")
        return False


def create_tables_via_api():
    """
    Attempt to create tables using Supabase Management API or RPC.
    Since direct SQL execution isn't available in the Python client,
    we'll provide SQL statements that can be run in Supabase SQL Editor.
    """
    print("\n" + "="*60)
    print("📋 DATABASE SETUP")
    print("="*60 + "\n")
    
    print("⚠️  Note: Supabase Python client doesn't support direct SQL execution.")
    print("📝 Please run the SQL statements below in Supabase SQL Editor.\n")
    print("📍 Go to: Supabase Dashboard → SQL Editor → New Query\n")
    
    all_sql = []
    
    for table_name, sql in TABLES_SQL.items():
        print(f"\n🔨 Table: {table_name}")
        all_sql.append(f"-- {table_name.upper()} TABLE\n{sql}\n")
        execute_sql(sql, table_name)
    
    # Create combined SQL file
    combined_sql = "\n".join(all_sql)
    
    # Save to file
    sql_file_path = "database_setup.sql"
    with open(sql_file_path, "w", encoding="utf-8") as f:
        f.write("-- ============================================\n")
        f.write("-- Job Application System Database Setup\n")
        f.write("-- Run this in Supabase SQL Editor\n")
        f.write("-- ============================================\n\n")
        f.write(combined_sql)
    
    print(f"\n✅ SQL statements saved to: {sql_file_path}")
    print(f"📋 Copy and paste the contents into Supabase SQL Editor\n")
    
    # Try to create storage buckets (if management API is available)
    print("\n" + "="*60)
    print("📦 STORAGE BUCKETS")
    print("="*60 + "\n")
    print("⚠️  Storage buckets must be created manually in Supabase Dashboard")
    print("📍 Go to: Storage → New Bucket\n")
    
    for bucket in STORAGE_BUCKETS:
        print(f"Bucket: {bucket['name']}")
        print(f"  Public: {bucket['public']}")
        print(f"  Description: {bucket['description']}\n")
    
    return True


def verify_tables_exist():
    """Verify if tables exist by attempting to query them."""
    print("\n" + "="*60)
    print("✅ VERIFICATION")
    print("="*60 + "\n")
    
    tables_to_check = ["applications", "networking_contacts", "resume_data"]
    
    for table_name in tables_to_check:
        try:
            # Try to query the table (with limit 0 to just check if it exists)
            result = supabase.table(table_name).select("*").limit(0).execute()
            print(f"✅ {table_name}: EXISTS")
        except Exception as e:
            error_msg = str(e)
            if "does not exist" in error_msg.lower() or "relation" in error_msg.lower():
                print(f"❌ {table_name}: DOES NOT EXIST")
                print(f"   Run the SQL statements above to create it.")
            else:
                print(f"⚠️  {table_name}: CHECK FAILED ({error_msg})")


def main():
    """Main function to set up database."""
    print("\n🚀 Setting up Supabase Database Tables...\n")
    
    # Create SQL file and provide instructions
    create_tables_via_api()
    
    # Verify existing tables
    verify_tables_exist()
    
    print("\n" + "="*60)
    print("📝 NEXT STEPS")
    print("="*60)
    print("1. Open Supabase Dashboard → SQL Editor")
    print("2. Copy contents from database_setup.sql")
    print("3. Paste and run in SQL Editor")
    print("4. Create storage buckets: resumes, screenshots")
    print("5. Run this script again to verify tables exist\n")


if __name__ == "__main__":
    main()

