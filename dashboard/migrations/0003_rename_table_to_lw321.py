from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_alter_loandata_options_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql='ALTER TABLE IF EXISTS loan_data RENAME TO "LW321";',
            reverse_sql='ALTER TABLE IF EXISTS "LW321" RENAME TO loan_data;',
        ),
    ]
