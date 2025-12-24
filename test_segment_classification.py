"""
Deep dive: Check if there are SMALL records not counted
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from dashboard.models import LW321
from dashboard.formulas.segmentation import get_segment_annotation
from django.db.models import Sum, Q, Case, When, Value, CharField, Count, Min, Max, Avg
from datetime import date
from decimal import Decimal

test_date = date(2025, 11, 30)
test_date_str = test_date.strftime('%d/%m/%Y')
KC_DEWI_SARTIKA = '286'

print(f"Deep dive into segment classification for KC {KC_DEWI_SARTIKA}")
print("=" * 80)

# Get records with segment annotation
qs = LW321.objects.filter(periode=test_date_str, kode_uker=KC_DEWI_SARTIKA)
qs = qs.annotate(segment=get_segment_annotation())

# Check ln_type distribution
print("\nDistribution by ln_type:")
ln_types = qs.values('ln_type').annotate(
    count=Count('id'),
    total_os=Sum('os')
).order_by('-total_os')

for item in ln_types[:10]:
    print(f"  {item['ln_type']}: {item['count']} records, OS={item['total_os']:,.0f}")

# Check segment assignment by ln_type
print("\nSegment assignment by ln_type:")
result = qs.values('ln_type', 'segment').annotate(
    count=Count('id'),
    total_os=Sum('os')
).order_by('ln_type', 'segment')

current_ln_type = None
for item in result:
    ln_type = item['ln_type'] or 'NULL'
    segment = item['segment'] or 'NULL'
    
    if ln_type != current_ln_type:
        print(f"\n{ln_type}:")
        current_ln_type = ln_type
    
    print(f"    → {segment}: {item['count']} records, OS={item['total_os']:,.0f}")

# Check if plafon is the issue
print(f"\n{'='*80}")
print("Checking plafon ranges:")

plafon_stats = qs.aggregate(
    min_plafon=Min('plafon'),
    max_plafon=Max('plafon'),
    avg_plafon=Avg('plafon')
)

print(f"Plafon range: {plafon_stats['min_plafon']:,.0f} - {plafon_stats['max_plafon']:,.0f}")
print(f"Average plafon: {plafon_stats['avg_plafon']:,.0f}")

# Check records near 5 billion threshold (SMALL vs MEDIUM cutoff)
threshold = 5000000000  # 5 billion
near_threshold = qs.filter(
    Q(plafon__gte=threshold - 500000000) & Q(plafon__lte=threshold + 500000000)
)

print(f"\nRecords near 5B threshold (4.5B - 5.5B): {near_threshold.count()}")
for rec in near_threshold[:10]:
    print(f"  Plafon: {rec.plafon:,.0f}, OS: {rec.os:,.0f}, Segment: {rec.segment}, ln_type: {rec.ln_type}")
