"""
Check uploaded data
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from dashboard.models import LW321

print("=" * 70)
print("CHECKING UPLOADED DATA")
print("=" * 70)

# Get last 3 records (newest uploads)
records = LW321.objects.all().order_by('-id')[:3]

for i, record in enumerate(records, 1):
    print(f"\nRecord #{i}:")
    print(f"  ID: {record.id}")
    print(f"  Nomor Rekening: {record.nomor_rekening}")
    print(f"  Periode: '{record.periode}'")
    print(f"  TGL REALISASI: '{record.tgl_realisasi}'")
    print(f"  TGL JATUH TEMPO: '{record.tgl_jatuh_tempo}'")
    print(f"  TGL MENUNGGAK: '{record.tgl_menunggak}'")
    print(f"  NEXT PMT DATE: '{record.next_pmt_date}'")
    print(f"  NEXT INT PMT DATE: '{record.next_int_pmt_date}'")
    print(f"  JANGKA WAKTU: '{record.jangka_waktu}'")
    print(f"  NASABAH: {record.nasabah}")
    print(f"  DUB NASABAH: '{record.dub_nasabah}'")
    print(f"  RATE: {record.rate}")

print("\n" + "=" * 70)
print(f"Total records in database: {LW321.objects.count()}")
print("=" * 70)
