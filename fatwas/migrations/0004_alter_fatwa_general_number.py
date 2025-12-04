from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('fatwas', '0003_alter_fatwa_department'),
    ]

    operations = [
        # Step 1: Drop any existing indexes on general_number
        migrations.RunSQL(
            sql="""
                DROP INDEX IF EXISTS fatwas_fatw_general_76b263_idx;
                DROP INDEX IF EXISTS fatwas_fatwa_general_number_idx;
            """,
            reverse_sql=migrations.RunSQL.noop
        ),
        
        # Step 2: Temporarily drop the unique constraint if exists
        migrations.RunSQL(
            sql="""
                ALTER TABLE fatwas_fatwa DROP CONSTRAINT IF EXISTS fatwas_fatwa_general_number_key;
            """,
            reverse_sql=migrations.RunSQL.noop
        ),

        # Step 3: Change column type from integer to varchar safely
        migrations.RunSQL(
            sql="""
                ALTER TABLE fatwas_fatwa 
                ALTER COLUMN general_number TYPE VARCHAR(50) USING general_number::varchar;
            """,
            reverse_sql=migrations.RunSQL.noop
        ),

        # Step 4: Re-add unique constraint
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
            field=models.CharField(
                max_length=50,
                blank=True,
                null=True,
                unique=True,
                verbose_name='الرقم العام'
            ),
        ),
    ]
