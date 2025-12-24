"""
Quick test NSB calculation with case-insensitive filter
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from dashboard.models import LW321
from django.db.models import Q, Sum
from dashboard.formulas.segmentation import get_segment_annotation
from dashboard.formulas.calculations import count_unique_customers

print("\n" + "="*80)
print("TEST CASE-INSENSITIVE DUB_NASABAH FILTER")
print("="*80)

# Check data variations
print("\nData variations in DUB_NASABAH:")
variations = LW321.objects.values('dub_nasabah').annotate(
    count=Sum('nasabah')
).order_by('dub_nasabah')[:10]

for v in variations:
    print(f"  '{v['dub_nasabah']}': {v['count']} records")

# Test case-insensitive filter
print("\n" + "="*80)
print("Manual Query Test:")
result = LW321.objects.annotate(
    segment=get_segment_annotation()
).filter(
    segment='SMALL'
).filter(
    Q(dub_nasabah__iexact='TRUE')
).aggregate(
    total=Sum('nasabah')
)

print(f"  Segment: SMALL")
print(f"  Filter: dub_nasabah__iexact='TRUE'")
print(f"  Result: {result['total']}")

# Test function
print("\nFunction Test:")
queryset = LW321.objects.all()
func_result = count_unique_customers(queryset, segment='SMALL')
print(f"  count_unique_customers(): {func_result}")

# Match check
print("\n" + "="*80)
if result['total'] == func_result:
    print("✅ PASS - Filter works correctly!")
else:
    print("❌ FAIL - Results don't match")
print("="*80 + "\n")
