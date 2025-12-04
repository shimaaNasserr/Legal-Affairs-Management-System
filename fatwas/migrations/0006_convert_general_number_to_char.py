# fatwas/migrations/000X_convert_general_number_to_char.py
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('fatwas', '0005_alter_fatwa_options_alter_fatwa_created_at_and_more'),
    ]

    operations = [
        # Step 1: Drop any existing indexes on general_number (they may have integer type)
        migrations.RunSQL(
            sql="""
                DROP INDEX IF EXISTS fatwas_fatw_general_76b263_idx;
                DROP INDEX IF EXISTS fatwas_fatwa_general_number_idx;
            """,
            reverse_sql=migrations.RunSQL.noop
        ),
        # Step 2: Drop unique constraint if exists
        migrations.RunSQL(
            sql="ALTER TABLE fatwas_fatwa DROP CONSTRAINT IF EXISTS fatwas_fatwa_general_number_key;",
            reverse_sql=migrations.RunSQL.noop
        ),
        # Step 3: Convert integer column to varchar
        migrations.RunSQL(
            sql="ALTER TABLE fatwas_fatwa ALTER COLUMN general_number TYPE VARCHAR(50) USING general_number::varchar;",
            reverse_sql=migrations.RunSQL.noop
        ),
        # Step 4: Recreate unique constraint
        migrations.RunSQL(
            sql="ALTER TABLE fatwas_fatwa ADD CONSTRAINT fatwas_fatwa_general_number_key UNIQUE (general_number);",
            reverse_sql=migrations.RunSQL.noop
        ),
        # Update Django model state
        migrations.AlterField(
            model_name='fatwa',
            name='general_number',
            field=models.CharField(
                max_length=50,
                unique=True,
                blank=True,
                null=True,
                verbose_name='الرقم العام'
            ),
        ),
    ]
