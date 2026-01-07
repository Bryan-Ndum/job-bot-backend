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

