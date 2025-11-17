from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_rename_table_to_lw321'),
    ]

    operations = [
        migrations.RunSQL(
            sql='ALTER TABLE IF EXISTS "LW321" RENAME TO lw321;',
            reverse_sql='ALTER TABLE IF EXISTS lw321 RENAME TO "LW321";',
        ),
    ]
