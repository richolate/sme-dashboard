"""
Check the latest uploaded data after Celery worker restart
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from dashboard.models import LW321

# Get the 5 most recent records
latest_records = LW321.objects.all().order_by('-id')[:5]

print("\n" + "="*80)
print("LATEST 5 RECORDS AFTER CELERY RESTART")
print("="*80)

for i, record in enumerate(latest_records, 1):
    print(f"\n--- Record #{i} (ID: {record.id}) ---")
    print(f"TGL_REALISASI    : {repr(record.tgl_realisasi)}")
    print(f"TGL_JATUH_TEMPO  : {repr(record.tgl_jatuh_tempo)}")
    print(f"TGL_MENUNGGAK    : {repr(record.tgl_menunggak)}")
    print(f"NEXT_PMT_DATE    : {repr(record.next_pmt_date)}")
    print(f"JANGKA_WAKTU     : {repr(record.jangka_waktu)}")
    print(f"NASABAH          : {repr(record.nasabah)}")
    print(f"DUB_NASABAH      : {repr(record.dub_nasabah)}")
    print(f"RATE             : {repr(record.rate)}")
    print(f"KANCA            : {repr(record.kanca)}")

print("\n" + "="*80)
print("Expected Formats:")
print("- Dates: 'MM/DD/YYYY' (e.g., '11/28/2025')")
print("- Empty dates: '' (empty string)")
print("- JANGKA_WAKTU: e.g., '106M' (if in Excel)")
print("- NASABAH: Decimal number (if in Excel)")
print("- DUB_NASABAH: 'TRUE' or 'FALSE' (if in Excel)")
print("="*80 + "\n")
