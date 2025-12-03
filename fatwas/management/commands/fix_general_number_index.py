"""
Management command to fix the general_number index issue
This drops and recreates the index with the correct VARCHAR type
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Fix the general_number column by converting it to INTEGER and recreating the index'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Fixing general_number index...'))
        
        with connection.cursor() as cursor:
            try:
                # Step 1: Drop the problematic index
                self.stdout.write('Dropping old index...')
                cursor.execute("DROP INDEX IF EXISTS fatwas_fatw_general_76b263_idx;")
                cursor.execute("DROP INDEX IF EXISTS fatwas_fatwa_general_number_idx;")
                self.stdout.write(self.style.SUCCESS('Old index dropped'))
                
                # Step 2: Check if column type needs to be changed
                cursor.execute("""
                    SELECT data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'fatwas_fatwa' 
                    AND column_name = 'general_number';
                """)
                result = cursor.fetchone()
                
                if result and result[0] == 'character varying':
                    self.stdout.write(self.style.WARNING('Column type is VARCHAR, converting to INTEGER...'))
                    # Clear any non-numeric values
                    cursor.execute("UPDATE fatwas_fatwa SET general_number = NULL WHERE general_number IS NOT NULL AND general_number !~ '^[0-9]+$';")
                    # Drop unique constraint temporarily
                    cursor.execute("ALTER TABLE fatwas_fatwa DROP CONSTRAINT IF EXISTS fatwas_fatwa_general_number_key;")
                    # Convert column type to integer
                    cursor.execute("ALTER TABLE fatwas_fatwa ALTER COLUMN general_number TYPE INTEGER USING CASE WHEN general_number ~ '^[0-9]+$' THEN general_number::integer ELSE NULL END;")
                    # Re-add unique constraint
                    cursor.execute("ALTER TABLE fatwas_fatwa ADD CONSTRAINT fatwas_fatwa_general_number_key UNIQUE (general_number);")
                    self.stdout.write(self.style.SUCCESS('Column type converted to INTEGER'))
                else:
                    self.stdout.write(self.style.SUCCESS('Column type is already INTEGER'))
                
                # Step 3: Recreate the index with correct type
                self.stdout.write('Recreating index with correct type...')
                cursor.execute("CREATE INDEX IF NOT EXISTS fatwas_fatw_general_76b263_idx ON fatwas_fatwa(general_number);")
                self.stdout.write(self.style.SUCCESS('Index recreated successfully'))
                
                self.stdout.write(self.style.SUCCESS('\nFixed! The general_number column is now INTEGER and the index has been recreated.'))
                self.stdout.write(self.style.SUCCESS('You can now create new fatwas with integer general_number values.'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
                raise

