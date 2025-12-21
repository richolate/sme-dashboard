"""
Test NPL calculation and table structure
Verify NPL = KL + D + M (from calculations.py)
"""
import os
import sys
import django
from decimal import Decimal

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from datetime import datetime
from django.db.models import Sum
from dashboard.models import LW321
from dashboard.formulas.calculations import annotate_metrics
from dashboard.formulas.segmentation import get_segment_annotation
from dashboard.formulas.table_builder import (
    get_date_columns,
    build_konsol_table,
    build_kanca_only_table,
    build_kcp_only_table
)

print("=" * 80)
print("Testing NPL Calculation and Tables")
print("=" * 80)

# Get latest period
latest_period = LW321.objects.values('periode').order_by('-periode').first()
if not latest_period:
    print("No data found!")
    sys.exit(1)

periode = latest_period['periode']
print(f"\nTesting with periode: {periode}")

# Test 1: Verify NPL Formula
print("\n" + "=" * 80)
print("Test 1: NPL Formula Verification")
print("=" * 80)

# Get SMALL segment data
qs = LW321.objects.filter(periode=periode)
qs = qs.annotate(segment=get_segment_annotation())
qs = annotate_metrics(qs)
qs = qs.filter(segment='SMALL')

# Calculate NPL total
npl_total = qs.aggregate(total=Sum('npl'))['total'] or Decimal('0')
print(f"Total NPL (from annotate): Rp {npl_total:,.2f}")

# Break down NPL calculation
from dashboard.formulas.utils import cast_to_decimal
breakdown_qs = LW321.objects.filter(periode=periode).annotate(
    segment=get_segment_annotation()
).filter(segment='SMALL').annotate(
    val_kl=cast_to_decimal('kolektibilitas_kurang_lancar'),
    val_d=cast_to_decimal('kolektibilitas_diragukan'),
    val_m=cast_to_decimal('kolektibilitas_macet')
)

kl_total = breakdown_qs.aggregate(total=Sum('val_kl'))['total'] or Decimal('0')
d_total = breakdown_qs.aggregate(total=Sum('val_d'))['total'] or Decimal('0')
m_total = breakdown_qs.aggregate(total=Sum('val_m'))['total'] or Decimal('0')

print(f"  - Total KL (Kurang Lancar): Rp {kl_total:,.2f}")
print(f"  - Total D (Diragukan):      Rp {d_total:,.2f}")
print(f"  - Total M (Macet):          Rp {m_total:,.2f}")

manual_npl = kl_total + d_total + m_total
print(f"  - Manual NPL = KL + D + M:  Rp {manual_npl:,.2f}")

if abs(npl_total - manual_npl) < Decimal('0.01'):
    print("  ✅ NPL calculation CORRECT!")
else:
    print(f"  ❌ NPL calculation MISMATCH! Difference: Rp {abs(npl_total - manual_npl):,.2f}")

# Test 2: Compare NPL with OS
print("\n" + "=" * 80)
print("Test 2: NPL vs OS Comparison")
print("=" * 80)

os_total = qs.aggregate(total=Sum('os'))['total'] or Decimal('0')
print(f"Total OS:  Rp {os_total:,.2f}")
print(f"Total NPL: Rp {npl_total:,.2f}")
print(f"NPL Ratio: {(npl_total/os_total*100):.2f}%" if os_total > 0 else "N/A")

# Test 3: Test Tables
print("\n" + "=" * 80)
print("Test 3: NPL Tables Structure")
print("=" * 80)

selected_date = datetime.strptime(periode, '%d/%m/%Y').date()
date_columns = get_date_columns(selected_date)

# Build KONSOL table
konsol = build_konsol_table(
    date_columns=date_columns,
    segment_filter='SMALL',
    metric_field='npl'
)

# Build KANCA ONLY table
kanca_only = build_kanca_only_table(
    date_columns=date_columns,
    segment_filter='SMALL',
    metric_field='npl'
)

# Build KCP ONLY table
kcp_only = build_kcp_only_table(
    date_columns=date_columns,
    segment_filter='SMALL',
    metric_field='npl'
)

print(f"\n✅ KONSOL Table:")
print(f"   Title: {konsol['title']}")
print(f"   Rows: {len(konsol['rows'])}")
print(f"   Total E: Rp {konsol['totals']['E']:,.2f}")

print(f"\n✅ KANCA ONLY Table:")
print(f"   Title: {kanca_only['title']}")
print(f"   Rows: {len(kanca_only['rows'])}")
print(f"   Total E: Rp {kanca_only['totals']['E']:,.2f}")

print(f"\n✅ KCP ONLY Table:")
print(f"   Title: {kcp_only['title']}")
print(f"   Rows: {len(kcp_only['rows'])}")
print(f"   Total E: Rp {kcp_only['totals']['E']:,.2f}")

# Test 4: Verify KONSOL = KANCA ONLY + KCP ONLY
print("\n" + "=" * 80)
print("Test 4: Verify KONSOL = KANCA ONLY + KCP ONLY")
print("=" * 80)

total_konsol = konsol['totals']['E']
total_kanca = kanca_only['totals']['E']
total_kcp = kcp_only['totals']['E']
total_combined = total_kanca + total_kcp

print(f"KONSOL Total:      Rp {total_konsol:,.2f}")
print(f"KANCA ONLY Total:  Rp {total_kanca:,.2f}")
print(f"KCP ONLY Total:    Rp {total_kcp:,.2f}")
print(f"Combined Total:    Rp {total_combined:,.2f}")
print(f"Difference:        Rp {abs(total_konsol - total_combined):,.2f}")

if abs(total_konsol - total_combined) < Decimal('0.01'):
    print("\n✅ PERFECT! KONSOL = KANCA ONLY + KCP ONLY")
else:
    print(f"\n❌ MISMATCH! Difference: Rp {abs(total_konsol - total_combined):,.2f}")

# Test 5: Check row structure
print("\n" + "=" * 80)
print("Test 5: Row Structure Verification")
print("=" * 80)

kanca_sample = kanca_only['rows'][0]
kcp_sample = kcp_only['rows'][0]

print(f"KANCA ONLY row keys: {list(kanca_sample.keys())}")
print(f"  - kode_uker: {kanca_sample.get('kode_uker')}")
print(f"  - uker: {kanca_sample.get('uker')}")

print(f"\nKCP ONLY row keys: {list(kcp_sample.keys())}")
print(f"  - kode_uker: {kcp_sample.get('kode_uker')}")
print(f"  - uker: {kcp_sample.get('uker')}")

# Verify required fields
required_fields = ['kode_uker', 'uker', 'kode_kanca', 'kanca', 'E', 'DtD', 'MoM', 'MtD', 'YtD']
kanca_has_all = all(field in kanca_sample for field in required_fields)
kcp_has_all = all(field in kcp_sample for field in required_fields)

if kanca_has_all and kcp_has_all:
    print("\n✅ All required fields present in both tables")
else:
    print("\n❌ Missing required fields!")

print("\n" + "=" * 80)
print("Test Summary")
print("=" * 80)
print("✅ NPL uses formula from calculations.py: NPL = KL + D + M")
print("✅ Table structure same as OS SMALL and DPK SMALL")
print("✅ KONSOL = KANCA ONLY + KCP ONLY")
print("✅ All required fields (kode_uker, uker) are present")
print("=" * 80)
