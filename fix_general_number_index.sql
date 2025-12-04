-- SQL script to fix the general_number index issue
-- This drops the problematic index and recreates it with the correct type
-- Run this directly on your PostgreSQL database

-- Step 1: Drop the problematic index that was created with integer type
DROP INDEX IF EXISTS fatwas_fatw_general_76b263_idx;
DROP INDEX IF EXISTS fatwas_fatwa_general_number_idx;

-- Step 2: Verify the column is already VARCHAR (if not, run the column type change)
-- If the column is still integer, uncomment and run this:
-- ALTER TABLE fatwas_fatwa DROP CONSTRAINT IF EXISTS fatwas_fatwa_general_number_key;
-- ALTER TABLE fatwas_fatwa ALTER COLUMN general_number TYPE VARCHAR(50) USING general_number::varchar;
-- ALTER TABLE fatwas_fatwa ADD CONSTRAINT fatwas_fatwa_general_number_key UNIQUE (general_number);

-- Step 3: Recreate the index with the correct VARCHAR type
CREATE INDEX IF NOT EXISTS fatwas_fatw_general_76b263_idx ON fatwas_fatwa(general_number);

