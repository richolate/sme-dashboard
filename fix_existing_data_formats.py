"""
Script untuk fix existing data:
1. Convert TGL REALISASI, TGL JATUH TEMPO, TGL MENUNGGAK dari YYYY-MM-DD ke MM/DD/YYYY
2. Convert nilai 0 atau 1970-01-01 menjadi empty string
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from dashboard.models import LW321
from datetime import datetime

def fix_date_formats():
    """Fix date formats in existing data"""
    print("=" * 70)
    print("FIXING DATE FORMATS IN EXISTING DATA")
    print("=" * 70)
    
    date_fields = ['tgl_realisasi', 'tgl_jatuh_tempo', 'tgl_menunggak', 'next_pmt_date', 'next_int_pmt_date']
    
    total_records = LW321.objects.count()
    print(f"\nTotal records to process: {total_records}")
    
    updated_count = 0
    batch_size = 1000
    
    for field_name in date_fields:
        print(f"\nProcessing field: {field_name.upper()}")
        print("-" * 70)
        
        # Get all records
        records = LW321.objects.all()
        batch = []
        
        for record in records:
            current_value = getattr(record, field_name)
            
            # Skip if already None or empty
            if not current_value or current_value == '':
                continue
            
            original_value = current_value
            new_value = current_value
            
            # Handle 1970-01-01 (Unix epoch - indicates 0)
            if '1970-01-01' in str(current_value):
                new_value = ''
                setattr(record, field_name, new_value)
                batch.append(record)
                continue
            
            # Handle date format conversion YYYY-MM-DD -> MM/DD/YYYY
            if isinstance(current_value, str):
                # Check if it's YYYY-MM-DD format
                if len(current_value) == 10 and current_value[4] == '-' and current_value[7] == '-':
                    try:
                        # Parse YYYY-MM-DD
                        dt = datetime.strptime(current_value, '%Y-%m-%d')
                        # Convert to MM/DD/YYYY
                        new_value = dt.strftime('%m/%d/%Y')
                        setattr(record, field_name, new_value)
                        batch.append(record)
                    except ValueError:
                        # If parsing fails, skip
                        pass
            
            # Batch update
            if len(batch) >= batch_size:
                LW321.objects.bulk_update(batch, [field_name])
                updated_count += len(batch)
                print(f"  Updated {updated_count} records...", end='\r')
                batch = []
        
        # Update remaining records
        if batch:
            LW321.objects.bulk_update(batch, [field_name])
            updated_count += len(batch)
        
        print(f"  ✅ Completed {field_name}: {updated_count} records updated")
    
    print("\n" + "=" * 70)
    print(f"TOTAL UPDATED: {updated_count} field values")
    print("=" * 70)


def show_sample_after_fix():
    """Show sample data after fix"""
    print("\n" + "=" * 70)
    print("SAMPLE DATA AFTER FIX")
    print("=" * 70)
    
    samples = LW321.objects.all()[:5]
    
    for i, record in enumerate(samples, 1):
        print(f"\nRecord #{i}:")
        print(f"  Nomor Rekening: {record.nomor_rekening}")
        print(f"  TGL REALISASI: '{record.tgl_realisasi}'")
        print(f"  TGL JATUH TEMPO: '{record.tgl_jatuh_tempo}'")
        print(f"  TGL MENUNGGAK: '{record.tgl_menunggak}'")
        print(f"  NEXT PMT DATE: '{record.next_pmt_date}'")
        print(f"  JANGKA WAKTU: '{record.jangka_waktu}'")
        print(f"  NASABAH: {record.nasabah}")
        print(f"  DUB NASABAH: '{record.dub_nasabah}'")


if __name__ == '__main__':
    fix_date_formats()
    show_sample_after_fix()
