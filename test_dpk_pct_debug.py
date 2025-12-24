"""
Debug script to check %DPK calculation
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from datetime import datetime
from django.db.models import Sum, Count
from dashboard.models import LW321
from dashboard.formulas.segmentation import get_segment_annotation
from dashboard.formulas.calculations import annotate_metrics

# Get today's date
today = datetime.now().date()
today_str = today.strftime('%d/%m/%Y')

print(f"Testing %DPK for date: {today_str}")
print("=" * 80)

# Get base data
qs = LW321.objects.filter(periode=today_str)
total_records = qs.count()
print(f"Total records for {today_str}: {total_records}")

if total_records == 0:
    print("\n❌ No data found for today!")
    print("Checking available dates...")
    available_dates = LW321.objects.values_list('periode', flat=True).distinct().order_by('-periode')[:5]
    print(f"Available dates: {list(available_dates)}")
    
    if available_dates:
        # Use the latest date
        latest_date_str = available_dates[0]
        print(f"\nUsing latest date: {latest_date_str}")
        qs = LW321.objects.filter(periode=latest_date_str)
        total_records = qs.count()
        print(f"Total records for {latest_date_str}: {total_records}")
    else:
        print("\n❌ No data in database at all!")
        exit(1)

# Annotate with segment and metrics
qs = qs.annotate(segment=get_segment_annotation())
qs = annotate_metrics(qs)

# Filter SMALL segment
qs_small = qs.filter(segment='SMALL')
print(f"\nTotal SMALL segment records: {qs_small.count()}")

# Check kol_adk distribution
print("\nKOL_ADK Distribution:")
kol_adk_dist = qs_small.values('kol_adk').annotate(count=Count('id')).order_by('kol_adk')
for item in kol_adk_dist:
    print(f"  kol_adk='{item['kol_adk']}': {item['count']} records")

# Check if there are kol_adk='2' records
kol_2_count = qs_small.filter(kol_adk='2').count()
print(f"\n✓ Records with kol_adk='2': {kol_2_count}")

# Get sample record with kol_adk='2'
if kol_2_count > 0:
    sample = qs_small.filter(kol_adk='2').first()
    print(f"\nSample record with kol_adk='2':")
    print(f"  UKER: {sample.kode_uker}")
    print(f"  Kanca: {sample.kanca}")
    print(f"  OS: {sample.os}")
    print(f"  Kolektibilitas DPK: {sample.kolektibilitas_dpk}")
    print(f"  KOL_ADK: {sample.kol_adk}")

# Test SML calculation
print("\n" + "=" * 80)
print("Testing SML (DPK) calculation per UKER:")
print("=" * 80)

result = qs_small.values('kode_uker', 'kanca').annotate(
    total_sml=Sum('sml'),
    total_os=Sum('os'),
    count=Count('id')
).order_by('kanca')[:5]  # Show first 5 UKER

for item in result:
    sml = item['total_sml'] or 0
    os = item['total_os'] or 0
    pct = (sml / os * 100) if os > 0 else 0
    print(f"UKER {item['kode_uker']} ({item['kanca']}):")
    print(f"  DPK: {sml:,.2f}")
    print(f"  OS: {os:,.2f}")
    print(f"  %DPK: {pct:.2f}%")
    print(f"  Records: {item['count']}")
    print()

# Test with annotate_metrics to verify sml field
print("=" * 80)
print("Checking individual records to verify SML annotation:")
print("=" * 80)

sample_records = qs_small.filter(kol_adk='2')[:3]
for rec in sample_records:
    print(f"Record ID {rec.id}:")
    print(f"  kode_uker: {rec.kode_uker}")
    print(f"  kol_adk: {rec.kol_adk}")
    print(f"  os: {rec.os}")
    print(f"  kolektibilitas_dpk: {rec.kolektibilitas_dpk}")
    print(f"  sml (annotated): {rec.sml}")
    print()

print("✅ Debug test completed!")
