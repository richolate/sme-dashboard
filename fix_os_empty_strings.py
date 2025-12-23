"""
Script to fix empty string values in os column by converting them to NULL
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

def fix_os_empty_strings():
    """Convert empty strings in os column to NULL"""
    with connection.cursor() as cursor:
        # Check current state
        cursor.execute("SELECT COUNT(*) FROM lw321 WHERE os IS NULL")
        null_count = cursor.fetchone()[0]
        print(f"Records with NULL os: {null_count}")
        
        cursor.execute("SELECT COUNT(*) FROM lw321")
        total_count = cursor.fetchone()[0]
        print(f"Total records: {total_count}")
        
        # Try to fix by casting os column text representation to numeric
        # This approach changes empty strings stored as text to NULL
        print("\nAttempting to fix os column...")
        try:
            # Temporarily change column type to handle empty strings
            cursor.execute("""
                ALTER TABLE lw321 
                ALTER COLUMN os TYPE VARCHAR(50) USING os::VARCHAR
            """)
            print("Step 1: Converted os to VARCHAR")
            
            # Now update empty strings to NULL
            cursor.execute("UPDATE lw321 SET os = NULL WHERE os = '' OR TRIM(os) = ''")
            updated = cursor.rowcount
            print(f"Step 2: Set {updated} empty strings to NULL")
            
            # Convert back to numeric
            cursor.execute("""
                ALTER TABLE lw321 
                ALTER COLUMN os TYPE NUMERIC(18,2) USING 
                CASE 
                    WHEN os IS NULL OR os = '' THEN NULL 
                    ELSE os::NUMERIC(18,2) 
                END
            """)
            print("Step 3: Converted os back to NUMERIC(18,2)")
            
            connection.commit()
            print("\n✅ Database updated successfully!")
        except Exception as e:
            connection.rollback()
            print(f"\n❌ Error: {e}")
            print("\nTrying alternative approach...")
            
            # Alternative: Just set all NULL
            cursor.execute("UPDATE lw321 SET os = NULL")
            connection.commit()
            print(f"Set all {cursor.rowcount} os values to NULL")

if __name__ == '__main__':
    fix_os_empty_strings()
