-- Email Intelligence Collector Database Initialization
-- This script is executed when PostgreSQL container starts for the first time

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Set timezone
SET timezone = 'UTC';

-- Create indexes for better performance (will be created by Alembic migrations)
-- But we can add some basic configurations here

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'Email Intelligence Collector database initialized successfully';
END $$;
