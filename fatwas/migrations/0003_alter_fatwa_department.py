# Generated manually to fix foreign key type mismatch
# Changes department foreign key from departments.department (bigint) to accounts.Department (UUID)

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_department_accounts_de_name_4ee611_idx_and_more'),
        ('departments', '0001_initial'),
        ('fatwas', '0002_alter_fatwa_options_alter_fatwa_created_at_and_more'),
    ]

    operations = [
        # Step 1: Drop the old foreign key constraint
        migrations.RunSQL(
            sql="ALTER TABLE fatwas_fatwa DROP CONSTRAINT IF EXISTS fatwas_fatwa_department_id_fkey;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        
        # Step 2: Convert department_id column from bigint to UUID
        # Map old department IDs to new UUIDs by matching department names
        migrations.RunSQL(
            sql="""
                -- Create temporary UUID column
                ALTER TABLE fatwas_fatwa ADD COLUMN department_id_temp UUID;
                
                -- Map old department IDs to new UUIDs by matching names
                -- If a match is found, use it; otherwise use the first accounts department
                UPDATE fatwas_fatwa 
                SET department_id_temp = COALESCE(
                    (SELECT ad.id 
                     FROM accounts_department ad 
                     INNER JOIN departments_department dd ON ad.name = dd.name 
                     WHERE dd.id = fatwas_fatwa.department_id 
                     LIMIT 1),
                    (SELECT id FROM accounts_department LIMIT 1)
                );
                
                -- Drop old column
                ALTER TABLE fatwas_fatwa DROP COLUMN department_id;
                
                -- Rename temp column
                ALTER TABLE fatwas_fatwa RENAME COLUMN department_id_temp TO department_id;
                
                -- Make it NOT NULL
                ALTER TABLE fatwas_fatwa ALTER COLUMN department_id SET NOT NULL;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        
        # Step 3: Update Django's model state to reflect the new foreign key
        migrations.AlterField(
            model_name='fatwa',
            name='department',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='accounts.department',
                verbose_name='الإدارة'
            ),
        ),
        
        # Step 4: Add the new foreign key constraint
        migrations.RunSQL(
            sql="""
                ALTER TABLE fatwas_fatwa 
                ADD CONSTRAINT fatwas_fatwa_department_id_fkey 
                FOREIGN KEY (department_id) 
                REFERENCES accounts_department(id) 
                ON DELETE CASCADE;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]

