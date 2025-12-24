"""
Test NSB calculation with new formula:
NSB = SUM(NASABAH) WHERE segment=SMALL AND DUB_NASABAH='TRUE'
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from dashboard.models import LW321
from dashboard.formulas.calculations import count_unique_customers
from dashboard.formulas.segmentation import get_segment_annotation
from django.db.models import Sum, Q

print("\n" + "="*80)
print("TEST NSB CALCULATION - NEW FORMULA")
print("="*80)

# Get latest data
latest = LW321.objects.latest('id')
print(f"\nLatest record ID: {latest.id}")
print(f"Periode: {latest.periode}")

# Check sample data
print("\n--- Sample Records ---")
sample = LW321.objects.annotate(
    segment=get_segment_annotation()
).filter(segment='SMALL').values(
    'kode_uker', 'uker', 'nasabah', 'dub_nasabah'
)[:10]

for rec in sample:
    print(f"UKER: {rec['kode_uker']} | NASABAH: {rec['nasabah']} | DUB_NASABAH: {rec['dub_nasabah']}")

# Test new formula
print("\n" + "="*80)
print("NSB CALCULATION TEST")
print("="*80)

# Manual calculation
queryset = LW321.objects.all()
manual_qs = queryset.annotate(
    segment=get_segment_annotation()
).filter(
    segment='SMALL',
    dub_nasabah='TRUE'
)

manual_result = manual_qs.aggregate(
    total_nasabah=Sum('nasabah')
)

print(f"\nManual Query:")
print(f"  Filter: segment='SMALL' AND dub_nasabah='TRUE'")
print(f"  Count: {manual_qs.count()} records")
print(f"  SUM(NASABAH): {manual_result['total_nasabah'] or 0}")

# Using function
function_result = count_unique_customers(queryset, segment='SMALL')
print(f"\nFunction Result:")
print(f"  count_unique_customers(): {function_result}")

# Verify match
print("\n" + "="*80)
if manual_result['total_nasabah'] == function_result:
    print("✅ PASS - Manual calculation matches function result")
else:
    print("❌ FAIL - Results don't match!")
print("="*80)

# Show breakdown by UKER
print("\n--- NSB by UKER (TOP 10) ---")
uker_breakdown = manual_qs.values('kode_uker', 'uker').annotate(
    total_nasabah=Sum('nasabah')
).order_by('-total_nasabah')[:10]

for item in uker_breakdown:
    print(f"UKER {item['kode_uker']} ({item['uker']}): {item['total_nasabah']}")

print("\n")
