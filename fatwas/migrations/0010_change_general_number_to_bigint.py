# Change general_number from INTEGER to BIGINT to support larger values
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fatwas', '0009_convert_id_to_uuid'),
    ]

    operations = [
        # Change column type from INTEGER to BIGINT
        migrations.RunSQL(
            sql="""
                -- Drop unique constraint temporarily
                ALTER TABLE fatwas_fatwa DROP CONSTRAINT IF EXISTS fatwas_fatwa_general_number_key;
                
                -- Change column type to BIGINT
                ALTER TABLE fatwas_fatwa 
                ALTER COLUMN general_number TYPE BIGINT 
                USING general_number::bigint;
                
                -- Re-add unique constraint
                ALTER TABLE fatwas_fatwa 
                ADD CONSTRAINT fatwas_fatwa_general_number_key UNIQUE (general_number);
            """,
            reverse_sql=migrations.RunSQL.noop
        ),
        
        # Update Django model state
        migrations.AlterField(
            model_name='fatwa',
            name='general_number',
            field=models.BigIntegerField(
                blank=True,
                null=True,
                unique=True,
                verbose_name='الرقم العام'
            ),
        ),
    ]

