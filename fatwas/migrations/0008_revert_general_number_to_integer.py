# Revert general_number back to PositiveIntegerField
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fatwas', '0007_merge_20251203_1917'),
    ]

    operations = [
        # Step 1: Drop indexes and constraints
        migrations.RunSQL(
            sql="""
                DROP INDEX IF EXISTS fatwas_fatw_general_76b263_idx;
                ALTER TABLE fatwas_fatwa DROP CONSTRAINT IF EXISTS fatwas_fatwa_general_number_key;
            """,
            reverse_sql=migrations.RunSQL.noop
        ),
        # Step 2: Convert column back to integer if it's VARCHAR, otherwise keep as integer
        migrations.RunSQL(
            sql="""
                -- Only convert if column is VARCHAR, otherwise do nothing
                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name = 'fatwas_fatwa' 
                        AND column_name = 'general_number' 
                        AND data_type = 'character varying'
                    ) THEN
                        -- Clear non-numeric values first
                        UPDATE fatwas_fatwa 
                        SET general_number = NULL 
                        WHERE general_number IS NOT NULL 
                        AND general_number !~ '^[0-9]+$';
                        
                        -- Convert to integer
                        ALTER TABLE fatwas_fatwa 
                        ALTER COLUMN general_number TYPE INTEGER 
                        USING CASE 
                            WHEN general_number ~ '^[0-9]+$' THEN general_number::integer 
                            ELSE NULL 
                        END;
                    END IF;
                END $$;
            """,
            reverse_sql=migrations.RunSQL.noop
        ),
        # Step 3: Re-add unique constraint
        migrations.RunSQL(
            sql="""
                ALTER TABLE fatwas_fatwa 
                ADD CONSTRAINT fatwas_fatwa_general_number_key UNIQUE (general_number);
            """,
            reverse_sql=migrations.RunSQL.noop
        ),
        # Step 4: Update Django model state
        migrations.AlterField(
            model_name='fatwa',
            name='general_number',
            field=models.PositiveIntegerField(
                blank=True,
                null=True,
                unique=True,
                verbose_name='الرقم العام'
            ),
        ),
    ]

