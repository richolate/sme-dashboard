"""
Test script untuk koneksi database PostgreSQL
Jalankan: python test_db_connection.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection
from django.conf import settings


def test_database_connection():
    """Test koneksi ke PostgreSQL database"""
    
    print("=" * 60)
    print("Testing PostgreSQL Connection")
    print("=" * 60)
    
    # Print database settings (hide password)
    db_config = settings.DATABASES['default']
    print(f"\nDatabase Configuration:")
    print(f"  Engine   : {db_config['ENGINE']}")
    print(f"  Name     : {db_config['NAME']}")
    print(f"  User     : {db_config['USER']}")
    print(f"  Host     : {db_config['HOST']}")
    print(f"  Port     : {db_config['PORT']}")
    print(f"  Password : {'*' * len(db_config['PASSWORD'])}")
    print(f"  Password : {db_config['PASSWORD']}")
    
    # Test connection
    try:
        with connection.cursor() as cursor:
            # Get PostgreSQL version
            cursor.execute("SELECT version();")
            db_version = cursor.fetchone()[0]
            
            # Get database name
            cursor.execute("SELECT current_database();")
            db_name = cursor.fetchone()[0]
            
            # Get user
            cursor.execute("SELECT current_user;")
            db_user = cursor.fetchone()[0]
            
            print(f"\n✅ Connection Successful!")
            print(f"\nDatabase Info:")
            print(f"  Database : {db_name}")
            print(f"  User     : {db_user}")
            print(f"  Version  : {db_version[:80]}...")
            
            # List all tables
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            
            print(f"\nTables in database ({len(tables)} tables):")
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]};")
                count = cursor.fetchone()[0]
                print(f"  - {table[0]}: {count} rows")
            
            print("\n" + "=" * 60)
            print("✅ All tests passed!")
            print("=" * 60)
            
    except Exception as e:
        print(f"\n❌ Connection Failed!")
        print(f"Error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check PostgreSQL service is running")
        print("2. Verify database exists: CREATE DATABASE sme_dashboard;")
        print("3. Check username/password in .env file")
        print("4. Verify host and port (default: localhost:5432)")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    test_database_connection()
