# Generated migration to fix os column empty strings

from django.db import migrations


def fix_os_empty_strings(apps, schema_editor):
    """
    Convert os column from VARCHAR to NUMERIC and handle empty strings
    """
    db_alias = schema_editor.connection.alias
    
    # Use raw SQL to fix the data
    with schema_editor.connection.cursor() as cursor:
        # First, change column to VARCHAR temporarily
        cursor.execute("""
            ALTER TABLE lw321 
            ALTER COLUMN os TYPE VARCHAR(50) USING os::VARCHAR
        """)
        
        # Update empty strings to NULL
        cursor.execute("""
            UPDATE lw321 
            SET os = NULL 
            WHERE os = '' OR TRIM(COALESCE(os, '')) = ''
        """)
        
        # Convert back to NUMERIC, handling any remaining empty strings
        cursor.execute("""
            ALTER TABLE lw321 
            ALTER COLUMN os TYPE NUMERIC(18,2) USING 
            CASE 
                WHEN os IS NULL OR TRIM(os) = '' THEN NULL 
                ELSE os::NUMERIC(18,2) 
            END
        """)


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0008_add_os_and_pn_rm_fields'),
    ]

    operations = [
        migrations.RunPython(fix_os_empty_strings, migrations.RunPython.noop),
    ]
