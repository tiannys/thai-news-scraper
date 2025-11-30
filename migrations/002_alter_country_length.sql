-- Migration: Alter country column length
-- Date: 2025-11-30
-- Description: Increase country field from VARCHAR(2) to VARCHAR(50) to support 'GLOBAL' and other values

-- Alter the sources table
ALTER TABLE sources 
ALTER COLUMN country TYPE VARCHAR(50);

-- Verify the change
SELECT column_name, data_type, character_maximum_length 
FROM information_schema.columns 
WHERE table_name = 'sources' AND column_name = 'country';
