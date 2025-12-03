# Convert id column from bigint to UUID
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fatwas', '0008_revert_general_number_to_integer'),
    ]

    operations = [
        # Step 1: Drop primary key constraint temporarily
        migrations.RunSQL(
            sql="""
                ALTER TABLE fatwas_fatwa DROP CONSTRAINT IF EXISTS fatwas_fatwa_pkey;
            """,
            reverse_sql=migrations.RunSQL.noop
        ),
        
        # Step 2: Add temporary UUID column
        migrations.RunSQL(
            sql="""
                ALTER TABLE fatwas_fatwa ADD COLUMN id_temp UUID;
            """,
            reverse_sql=migrations.RunSQL.noop
        ),
        
        # Step 3: Generate UUIDs for existing records (if any)
        # Try gen_random_uuid() first (PostgreSQL 13+), fallback to uuid_generate_v4()
        migrations.RunSQL(
            sql="""
                -- Enable uuid extension if needed
                CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
                -- Generate UUIDs for existing records
                UPDATE fatwas_fatwa SET id_temp = uuid_generate_v4();
            """,
            reverse_sql=migrations.RunSQL.noop
        ),
        
        # Step 4: Drop old id column and rename temp column
        migrations.RunSQL(
            sql="""
                ALTER TABLE fatwas_fatwa DROP COLUMN id;
                ALTER TABLE fatwas_fatwa RENAME COLUMN id_temp TO id;
                ALTER TABLE fatwas_fatwa ALTER COLUMN id SET NOT NULL;
            """,
            reverse_sql=migrations.RunSQL.noop
        ),
        
        # Step 5: Re-add primary key constraint
        migrations.RunSQL(
            sql="""
                ALTER TABLE fatwas_fatwa ADD CONSTRAINT fatwas_fatwa_pkey PRIMARY KEY (id);
            """,
            reverse_sql=migrations.RunSQL.noop
        ),
        
        # Step 6: Update Django model state (already done in 0005, but ensuring it's correct)
        migrations.AlterField(
            model_name='fatwa',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]

