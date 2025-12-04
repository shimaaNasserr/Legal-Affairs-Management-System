from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('cases', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql='''
                ALTER TABLE cases
                ADD COLUMN hearing_dates_json jsonb DEFAULT '[]'::jsonb;
            ''',
            reverse_sql='''
                ALTER TABLE cases
                DROP COLUMN hearing_dates_json;
            '''
        ),
        migrations.RunSQL(
            sql='''
                UPDATE cases
                SET hearing_dates_json = '[]'::jsonb;
            ''',
            reverse_sql='''
                UPDATE cases
                SET hearing_dates_json = NULL;
            '''
        ),
        migrations.RunSQL(
            sql='''
                ALTER TABLE cases
                DROP COLUMN hearing_dates;
            ''',
            reverse_sql='''
                ALTER TABLE cases
                ADD COLUMN hearing_dates date[];
            '''
        ),
        migrations.RunSQL(
            sql='''
                ALTER TABLE cases
                RENAME COLUMN hearing_dates_json TO hearing_dates;
            ''',
            reverse_sql='''
                ALTER TABLE cases
                RENAME COLUMN hearing_dates TO hearing_dates_json;
            '''
        ),
    ]
