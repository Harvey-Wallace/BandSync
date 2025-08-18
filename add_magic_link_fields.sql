-- Add magic link authentication fields to User table
-- Safe to run multiple times (uses IF NOT EXISTS)

-- Add magic_link_token column
DO $$ 
BEGIN 
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'user' 
        AND column_name = 'magic_link_token'
    ) THEN
        ALTER TABLE "user" ADD COLUMN magic_link_token VARCHAR(255);
        RAISE NOTICE 'Added magic_link_token column';
    ELSE
        RAISE NOTICE 'magic_link_token column already exists';
    END IF;
END $$;

-- Add magic_link_expires column  
DO $$ 
BEGIN 
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'user' 
        AND column_name = 'magic_link_expires'
    ) THEN
        ALTER TABLE "user" ADD COLUMN magic_link_expires TIMESTAMP;
        RAISE NOTICE 'Added magic_link_expires column';
    ELSE
        RAISE NOTICE 'magic_link_expires column already exists';
    END IF;
END $$;

-- Verify the columns were added
SELECT 
    column_name, 
    data_type, 
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'user' 
AND column_name IN ('magic_link_token', 'magic_link_expires')
ORDER BY column_name;
