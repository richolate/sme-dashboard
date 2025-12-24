"""
Test script untuk verify field type changes
Test NASABAH dan DUB NASABAH fields, serta perubahan tipe data lainnya
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from dashboard.models import LW321
from decimal import Decimal

def test_field_types():
    """Test field types after migration"""
    print("=" * 70)
    print("TESTING FIELD TYPES AFTER MIGRATION")
    print("=" * 70)
    
    # Get field info from model
    print("\n📋 Field Information:")
    print("-" * 70)
    
    fields_to_check = [
        'periode', 'kanca', 'kode_uker', 'uker', 'ln_type',
        'nama_debitur', 'next_pmt_date', 'next_int_pmt_date',
        'rate', 'tgl_menunggak', 'tgl_realisasi', 'tgl_jatuh_tempo',
        'jangka_waktu', 'flag_restruk', 'kol_adk', 'pn_rm', 'nama_rm',
        'nasabah', 'dub_nasabah'
    ]
    
    for field_name in fields_to_check:
        field = LW321._meta.get_field(field_name)
        field_type = field.get_internal_type()
        
        # Get additional info
        info = []
        if hasattr(field, 'max_length') and field.max_length:
            info.append(f"max_length={field.max_length}")
        if hasattr(field, 'max_digits') and field.max_digits:
            info.append(f"max_digits={field.max_digits}")
        if hasattr(field, 'decimal_places') and field.decimal_places:
            info.append(f"decimal_places={field.decimal_places}")
        if field.null:
            info.append("null=True")
        if field.blank:
            info.append("blank=True")
        
        info_str = f" ({', '.join(info)})" if info else ""
        print(f"  {field_name:25} → {field_type:20}{info_str}")
    
    print("\n" + "=" * 70)
    print("TESTING EXISTING DATA")
    print("=" * 70)
    
    # Get sample records
    sample_records = LW321.objects.all()[:5]
    
    if not sample_records:
        print("\n⚠️  No data in database - skipping data tests")
    else:
        print(f"\n📊 Found {LW321.objects.count()} total records")
        print(f"   Showing first {len(sample_records)} records:\n")
        
        for i, record in enumerate(sample_records, 1):
            print(f"Record #{i}:")
            print(f"  Nomor Rekening: {record.nomor_rekening}")
            print(f"  Periode: {record.periode} (type: {type(record.periode).__name__})")
            print(f"  RATE: {record.rate} (type: {type(record.rate).__name__ if record.rate else 'None'})")
            print(f"  Next PMT Date: {record.next_pmt_date} (type: {type(record.next_pmt_date).__name__})")
            print(f"  Tgl Realisasi: {record.tgl_realisasi} (type: {type(record.tgl_realisasi).__name__})")
            print(f"  Jangka Waktu: {record.jangka_waktu} (type: {type(record.jangka_waktu).__name__})")
            print(f"  NASABAH: {record.nasabah} (type: {type(record.nasabah).__name__ if record.nasabah else 'None'})")
            print(f"  DUB NASABAH: {record.dub_nasabah} (type: {type(record.dub_nasabah).__name__ if record.dub_nasabah is not None else 'None'})")
            print()
    
    print("\n" + "=" * 70)
    print("FIELD TYPE VERIFICATION")
    print("=" * 70)
    
    # Check specific fields
    checks = []
    
    # Check VARCHAR fields
    periode_field = LW321._meta.get_field('periode')
    checks.append(("PERIODE length", periode_field.max_length == 20, f"Expected 20, got {periode_field.max_length}"))
    
    kanca_field = LW321._meta.get_field('kanca')
    checks.append(("KANCA length", kanca_field.max_length == 50, f"Expected 50, got {kanca_field.max_length}"))
    
    kode_uker_field = LW321._meta.get_field('kode_uker')
    checks.append(("KODE UKER length", kode_uker_field.max_length == 10, f"Expected 10, got {kode_uker_field.max_length}"))
    
    # Check date fields are now CharField
    next_pmt_field = LW321._meta.get_field('next_pmt_date')
    checks.append(("NEXT PMT DATE is CharField", next_pmt_field.get_internal_type() == 'CharField', f"Expected CharField, got {next_pmt_field.get_internal_type()}"))
    
    tgl_realisasi_field = LW321._meta.get_field('tgl_realisasi')
    checks.append(("TGL REALISASI is CharField", tgl_realisasi_field.get_internal_type() == 'CharField', f"Expected CharField, got {tgl_realisasi_field.get_internal_type()}"))
    
    # Check RATE precision
    rate_field = LW321._meta.get_field('rate')
    checks.append(("RATE decimal_places", rate_field.decimal_places == 2, f"Expected 2, got {rate_field.decimal_places}"))
    checks.append(("RATE max_digits", rate_field.max_digits == 5, f"Expected 5, got {rate_field.max_digits}"))
    
    # Check JANGKA WAKTU is CharField
    jangka_waktu_field = LW321._meta.get_field('jangka_waktu')
    checks.append(("JANGKA WAKTU is CharField", jangka_waktu_field.get_internal_type() == 'CharField', f"Expected CharField, got {jangka_waktu_field.get_internal_type()}"))
    
    # Check NASABAH exists
    nasabah_field = LW321._meta.get_field('nasabah')
    checks.append(("NASABAH is DecimalField", nasabah_field.get_internal_type() == 'DecimalField', f"Expected DecimalField, got {nasabah_field.get_internal_type()}"))
    
    # Check DUB NASABAH exists
    dub_nasabah_field = LW321._meta.get_field('dub_nasabah')
    checks.append(("DUB NASABAH is CharField", dub_nasabah_field.get_internal_type() == 'CharField', f"Expected CharField, got {dub_nasabah_field.get_internal_type()}"))
    checks.append(("DUB NASABAH max_length", dub_nasabah_field.max_length == 10, f"Expected 10, got {dub_nasabah_field.max_length}"))
    
    print()
    for check_name, passed, message in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {check_name}")
        if not passed:
            print(f"         {message}")
    
    print("\n" + "=" * 70)
    
    # Check for NASABAH and DUB NASABAH data
    if LW321.objects.count() > 0:
        print("\nCHECKING NASABAH AND DUB NASABAH DATA:")
        print("-" * 70)
        
        records_with_nasabah = LW321.objects.filter(nasabah__isnull=False).count()
        records_with_dub = LW321.objects.filter(dub_nasabah__isnull=False).count()
        total_records = LW321.objects.count()
        
        print(f"  Total Records: {total_records}")
        print(f"  Records with NASABAH: {records_with_nasabah}")
        print(f"  Records with DUB NASABAH: {records_with_dub}")
        
        if records_with_nasabah == 0:
            print("\n  ⚠️  WARNING: NASABAH field is empty for all records")
            print("     Action: Upload new file with NASABAH column")
        
        if records_with_dub == 0:
            print("\n  ⚠️  WARNING: DUB NASABAH field is empty for all records")
            print("     Action: Upload new file with DUB NASABAH column")
    
    print("\n" + "=" * 70)


if __name__ == '__main__':
    test_field_types()
