-- SQL script to fix general_number column type from integer to varchar
-- Run this directly on your PostgreSQL database

-- Step 1: Drop any existing indexes on general_number (they may have integer type)
DROP INDEX IF EXISTS fatwas_fatw_general_76b263_idx;
DROP INDEX IF EXISTS fatwas_fatwa_general_number_idx;

-- Step 2: Convert any existing integer values to strings
UPDATE fatwas_fatwa 
SET general_number = general_number::text 
WHERE general_number IS NOT NULL;

-- Step 3: Drop the unique constraint temporarily
ALTER TABLE fatwas_fatwa DROP CONSTRAINT IF EXISTS fatwas_fatwa_general_number_key;

-- Step 4: Change column type from integer to varchar
ALTER TABLE fatwas_fatwa 
ALTER COLUMN general_number TYPE VARCHAR(50) 
USING general_number::text;

-- Step 5: Re-add the unique constraint
ALTER TABLE fatwas_fatwa 
ADD CONSTRAINT fatwas_fatwa_general_number_key 
UNIQUE (general_number);

-- Step 6: Recreate the index with the correct type
CREATE INDEX IF NOT EXISTS fatwas_fatw_general_76b263_idx ON fatwas_fatwa(general_number);

