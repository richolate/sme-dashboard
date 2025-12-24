"""
Debug OS calculation for KC Bandung Dewi Sartika
Compare with screenshot: OS should be 270,775 (thousands)
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from dashboard.models import LW321
from dashboard.formulas.calculations import annotate_metrics
from dashboard.formulas.segmentation import get_segment_annotation
from dashboard.formulas.table_builder import get_metric_by_uker, get_metric_by_kanca, get_base_queryset, get_kode_kanca_from_uker
from dashboard.formulas.uker_mapping import KANCA_CODES
from datetime import date
from decimal import Decimal

# Test date from screenshot: 30-Nov-25
test_date = date(2025, 11, 30)
KC_DEWI_SARTIKA = '286'

print(f"Testing OS for KC Bandung Dewi Sartika ({KC_DEWI_SARTIKA})")
print(f"Date: {test_date}")
print("=" * 80)

# Method 1: Direct query
print("\n=== METHOD 1: Direct Database Query ===")
test_date_str = test_date.strftime('%d/%m/%Y')
qs = LW321.objects.filter(periode=test_date_str, kode_uker=KC_DEWI_SARTIKA)
qs = qs.annotate(segment=get_segment_annotation())
qs = annotate_metrics(qs)
records = qs.filter(segment='SMALL')

print(f"Total records: {records.count()}")
print("\nBreakdown by kol_adk:")
total_by_kol_adk = {}
for kol_adk in ['1', '2', '3', '4', '5']:
    kol_records = records.filter(kol_adk=kol_adk)
    total_os = sum(r.os or Decimal('0') for r in kol_records)
    total_by_kol_adk[kol_adk] = total_os
    print(f"  kol_adk='{kol_adk}': {kol_records.count()} records, OS={total_os:,.0f} ({total_os/1000:,.0f} thousand)")

total_os_all = sum(total_by_kol_adk.values())
print(f"\nTotal OS (all kol_adk): {total_os_all:,.0f} ({total_os_all/1000:,.0f} thousand)")

# Method 2: Using get_metric_by_uker (without kol_adk filter)
print("\n=== METHOD 2: get_metric_by_uker (no filter) ===")
os_by_uker = get_metric_by_uker(test_date, 'SMALL', 'os', kol_adk_filter=None)
os_286 = os_by_uker.get(KC_DEWI_SARTIKA, Decimal('0'))
print(f"OS for {KC_DEWI_SARTIKA}: {os_286:,.0f} ({os_286/1000:,.0f} thousand)")

# Method 3: Check if there's a kol_adk filter issue
print("\n=== METHOD 3: get_base_queryset analysis ===")
qs_base = get_base_queryset(test_date, 'SMALL', 'os', kol_adk_filter=None)
qs_filtered = qs_base.filter(kode_uker=KC_DEWI_SARTIKA)
print(f"Records from get_base_queryset: {qs_filtered.count()}")

# Group by kol_adk
from django.db.models import Sum
result = qs_filtered.values('kol_adk').annotate(total_os=Sum('os')).order_by('kol_adk')
print("Breakdown by kol_adk:")
for item in result:
    print(f"  kol_adk='{item['kol_adk']}': OS={item['total_os']:,.0f} ({item['total_os']/1000:,.0f} thousand)")

# Check get_metric_by_kanca for KANCA 181 (Bandung)
print("\n=== METHOD 4: Check KANCA 181 (Bandung) total ===")
os_by_kanca = get_metric_by_kanca(test_date, 'SMALL', 'os', kol_adk_filter=None)
os_181 = os_by_kanca.get(181, Decimal('0'))
print(f"OS for KANCA 181 (Bandung): {os_181:,.0f} ({os_181/1000:,.0f} thousand)")
print(f"Expected from screenshot: 12,217,992 thousand")

# Check all UKERs under KANCA 181
print("\n=== All UKERs under KANCA 181 ===")
all_os_by_uker = get_metric_by_uker(test_date, 'SMALL', 'os', kol_adk_filter=None)
kanca_181_total = Decimal('0')
for kode_uker, os_val in sorted(all_os_by_uker.items()):
    kode_kanca = get_kode_kanca_from_uker(str(kode_uker))
    if kode_kanca == 181:
        kanca_181_total += os_val
        if str(kode_uker) == KC_DEWI_SARTIKA:
            print(f"  >>> {kode_uker}: {os_val:,.0f} ({os_val/1000:,.0f} thousand) <<<")
        else:
            print(f"  {kode_uker}: {os_val:,.0f} ({os_val/1000:,.0f} thousand)")

print(f"\nTotal KANCA 181 (sum of all UKERs): {kanca_181_total:,.0f} ({kanca_181_total/1000:,.0f} thousand)")

print("\n" + "=" * 80)
print("EXPECTED from screenshot:")
print("  KC Bandung Dewi Sartika: 270,775 thousand")
print("  RO BANDUNG total: 12,217,992 thousand")
print("\nACTUAL from calculation:")
print(f"  KC Bandung Dewi Sartika: {os_286/1000:,.0f} thousand")
print(f"  RO BANDUNG total: {os_181/1000:,.0f} thousand")
