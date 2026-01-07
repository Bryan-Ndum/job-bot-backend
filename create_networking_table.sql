-- Create networking_contacts table
-- Run this in Supabase SQL Editor

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






