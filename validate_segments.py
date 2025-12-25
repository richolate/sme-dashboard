#!/usr/bin/env python
"""Check if SMALL segment still has data after reordering"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from dashboard.models import LW321
from dashboard.formulas.segmentation import get_segment_annotation, SEGMENT_MAPPING_BY_CODE
from django.db.models import Count, Sum

print("Validating segment changes...")
print("="*70)

# Check all segments
result = LW321.objects.annotate(
    segment=get_segment_annotation()
).values('segment').annotate(
    count=Count('id'),
    total_os=Sum('os')
).order_by('segment')

print("\n📊 ALL SEGMENTS:")
print("-"*70)
total_records = 0
total_os = 0
for r in result:
    os_val = r['total_os'] or 0
    total_records += r['count']
    total_os += os_val
    print(f"  {r['segment']:<15} : {r['count']:>7,} records | OS = {os_val:>22,.2f}")

print("-"*70)
print(f"  {'TOTAL':<15} : {total_records:>7,} records | OS = {total_os:>22,.2f}")

# Check SMALL specifically
print("\n"+ "="*70)
print("⚠️  CHECKING SMALL SEGMENT (should be 0 after reordering)")
print("-"*70)
small = LW321.objects.annotate(segment=get_segment_annotation()).filter(segment='SMALL')
small_count = small.count()
small_os = small.aggregate(total=Sum('os'))['total'] or 0

print(f"  SMALL records: {small_count:,}")
print(f"  SMALL OS: {small_os:,.2f}")

if small_count > 0:
    print("\n  ⚠️  WARNING: SMALL still has records!")
    print("  This is expected if there are SMALL codes that are NOT in SMALL NCC")
    print("\n  Sample SMALL codes found:")
    codes = small.values('code').annotate(count=Count('id')).order_by('-count')[:10]
    for c in codes:
        in_ncc = c['code'] in SEGMENT_MAPPING_BY_CODE.get('SMALL NCC', [])
        marker = "❌ SHOULD BE SMALL NCC!" if in_ncc else "✓ Correct (not in SMALL NCC)"
        print(f"    CODE {c['code']}: {c['count']:>6,} records  {marker}")
else:
    print("  ✓ Perfect! All SMALL codes moved to SMALL NCC")

print("\n" + "="*70)
print("✅ VALIDATION COMPLETE")
print("="*70)
