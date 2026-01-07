# Quick Database Setup Guide

## Current Status

✅ **applications** table: EXISTS  
❌ **networking_contacts** table: MISSING  
✅ **resume_data** table: EXISTS  

## Quick Fix - Create Missing Table

### Option 1: Copy-Paste SQL (Fastest)

1. Go to: https://supabase.com/dashboard
2. Select your project
3. Click: **SQL Editor** (left sidebar)
4. Click: **New Query**
5. Copy and paste this SQL:

```sql
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
```

6. Click: **Run** (or press Ctrl+Enter)

### Option 2: Use the SQL File

1. Open: `create_missing_tables.sql` (in project root)
2. Copy all contents
3. Paste in Supabase SQL Editor
4. Run

### Verify Tables Created

After running the SQL, verify by running:

```bash
python Scripts/create_missing_tables.py
```

You should see:
```
✓ applications: EXISTS
✓ networking_contacts: EXISTS
✓ resume_data: EXISTS
```

## All Tables SQL (Complete Setup)

If you want to ensure all tables are set up correctly, use `database_setup.sql`:

1. Open: `database_setup.sql`
2. Copy all contents
3. Paste in Supabase SQL Editor
4. Run (it uses `IF NOT EXISTS` so it's safe to run multiple times)

## Storage Buckets (Optional)

For file storage (resumes, screenshots), create buckets:

1. Go to: **Storage** (left sidebar)
2. Click: **New Bucket**
3. Create:
   - **Name**: `resumes` (Private)
   - **Name**: `screenshots` (Private)

These are optional - the system works without them, but they enable file storage in Supabase.






