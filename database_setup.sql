-- ============================================
-- Job Application System Database Setup
-- Run this in Supabase SQL Editor
-- ============================================

-- APPLICATIONS TABLE
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

-- Create indexes on applications
CREATE INDEX IF NOT EXISTS idx_applications_user_id ON applications(user_id);
CREATE INDEX IF NOT EXISTS idx_applications_application_id ON applications(application_id);
CREATE INDEX IF NOT EXISTS idx_applications_callback_status ON applications(callback_status);

-- NETWORKING_CONTACTS TABLE
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

-- Create indexes on networking_contacts
CREATE INDEX IF NOT EXISTS idx_networking_user_id ON networking_contacts(user_id);
CREATE INDEX IF NOT EXISTS idx_networking_application_id ON networking_contacts(application_id);

-- RESUME_DATA TABLE
CREATE TABLE IF NOT EXISTS resume_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dataset_name TEXT UNIQUE NOT NULL,
    content JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create index on resume_data
CREATE INDEX IF NOT EXISTS idx_resume_data_dataset_name ON resume_data(dataset_name);
