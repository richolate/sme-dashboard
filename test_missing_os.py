"""
Debug: Find missing 4 billion rupiah in KC Dewi Sartika
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from dashboard.models import LW321
from dashboard.formulas.calculations import annotate_metrics
from dashboard.formulas.segmentation import get_segment_annotation
from datetime import date
from decimal import Decimal

test_date = date(2025, 11, 30)
test_date_str = test_date.strftime('%d/%m/%Y')
KC_DEWI_SARTIKA = '286'

print(f"Finding missing OS for KC {KC_DEWI_SARTIKA}")
print("=" * 80)

# Get ALL records (without segment filter)
all_records = LW321.objects.filter(periode=test_date_str, kode_uker=KC_DEWI_SARTIKA)
print(f"\nTotal records (no filter): {all_records.count()}")

total_os_no_filter = sum(r.os or Decimal('0') for r in all_records)
print(f"Total OS (no filter): {total_os_no_filter:,.0f} ({total_os_no_filter/1000:,.0f} thousand)")

# Get records WITH segment annotation
qs = LW321.objects.filter(periode=test_date_str, kode_uker=KC_DEWI_SARTIKA)
qs = qs.annotate(segment=get_segment_annotation())

# Check segments
print(f"\nRecords by segment:")
for seg in ['SMALL', 'MEDIUM', 'CC', 'KUR', None]:
    if seg is None:
        seg_records = qs.filter(segment__isnull=True)
        label = "NULL/Unknown"
    else:
        seg_records = qs.filter(segment=seg)
        label = seg
    
    count = seg_records.count()
    if count > 0:
        total = sum(r.os or Decimal('0') for r in seg_records)
        print(f"  {label}: {count} records, OS={total:,.0f} ({total/1000:,.0f} thousand)")

# Get SMALL segment with metrics annotation
qs_small = LW321.objects.filter(periode=test_date_str, kode_uker=KC_DEWI_SARTIKA)
qs_small = qs_small.annotate(segment=get_segment_annotation())
qs_small = annotate_metrics(qs_small)
qs_small = qs_small.filter(segment='SMALL')

total_os_small = sum(r.os or Decimal('0') for r in qs_small)
print(f"\nTotal OS (SMALL with annotations): {total_os_small:,.0f} ({total_os_small/1000:,.0f} thousand)")

# Calculate difference
diff = total_os_no_filter - total_os_small
print(f"\nMissing OS: {diff:,.0f} ({diff/1000:,.0f} thousand)")

print(f"\n{'='*80}")
print("EXPECTED from screenshot: 270,775 thousand")
print(f"ACTUAL from database: {total_os_small/1000:,.0f} thousand")
print(f"Difference: {(270775000 - total_os_small) / 1000:,.0f} thousand")
