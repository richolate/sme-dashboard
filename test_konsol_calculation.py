"""
Script untuk memverifikasi perhitungan KONSOL table
Memastikan: KONSOL = KANCA ONLY + KCP ONLY
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from datetime import date
from dashboard.models import LW321
from dashboard.formulas import get_segment_annotation, annotate_metrics, KANCA_MASTER, UKER_MASTER, KANCA_CODES, KCP_CODES
from django.db.models import Sum

# Test date
test_date_str = "30/11/2025"

print(f"\n{'='*80}")
print(f"VERIFIKASI PERHITUNGAN KONSOL TABLE")
print(f"Tanggal: {test_date_str}")
print(f"{'='*80}\n")

# Get base queryset with annotations
qs = LW321.objects.all()
qs = qs.annotate(segment=get_segment_annotation())
qs = annotate_metrics(qs)

# Filter by date and segment
qs_filtered = qs.filter(periode=test_date_str, segment='SMALL')

# Get all OS by kode_uker
print("Step 1: Mengambil semua OS berdasarkan kode_uker...")
os_by_uker = {}
for row in qs_filtered.values('kode_uker').annotate(total_os=Sum('os')):
    kode_uker = row['kode_uker']
    total_os = float(row['total_os'] or 0)
    os_by_uker[kode_uker] = total_os
    print(f"  UKER {kode_uker}: {total_os:,.2f}")

print(f"\nTotal UKERs found: {len(os_by_uker)}")

# Helper function
def get_kode_kanca_from_uker(kode_uker_str):
    try:
        kode_uker = int(kode_uker_str)
    except (ValueError, TypeError):
        return None
    
    if kode_uker in KANCA_CODES:
        return kode_uker
    
    if kode_uker in UKER_MASTER:
        _, kode_kanca_induk = UKER_MASTER[kode_uker]
        return kode_kanca_induk
    
    for k, (n, induk) in UKER_MASTER.items():
        if k == kode_uker:
            return induk
    
    return None

# Group by KANCA (KONSOL)
print("\n" + "="*80)
print("Step 2: Grouping by KANCA (KONSOL METHOD)")
print("="*80)
os_by_kanca_konsol = {}
unmatched_ukers = []

for kode_uker_str, os_value in os_by_uker.items():
    kode_kanca = get_kode_kanca_from_uker(kode_uker_str)
    if kode_kanca:
        if kode_kanca not in os_by_kanca_konsol:
            os_by_kanca_konsol[kode_kanca] = 0
        os_by_kanca_konsol[kode_kanca] += os_value
    else:
        unmatched_ukers.append((kode_uker_str, os_value))

if unmatched_ukers:
    print("\n⚠️  WARNING: UKERs yang tidak ter-mapping ke KANCA:")
    for uker, value in unmatched_ukers:
        print(f"  UKER {uker}: {value:,.2f}")

# Get KANCA ONLY
print("\n" + "="*80)
print("Step 3: KANCA ONLY")
print("="*80)
kanca_codes_str = [str(c) for c in KANCA_CODES]
qs_kanca = qs_filtered.filter(kode_uker__in=kanca_codes_str)
os_kanca_only = {}
for row in qs_kanca.values('kode_uker').annotate(total_os=Sum('os')):
    kode_kanca = int(row['kode_uker'])
    os_kanca_only[kode_kanca] = float(row['total_os'] or 0)
    print(f"  KANCA {kode_kanca} ({KANCA_MASTER.get(kode_kanca, '?')}): {os_kanca_only[kode_kanca]:,.2f}")

# Get KCP ONLY
print("\n" + "="*80)
print("Step 4: KCP ONLY (grouped by parent KANCA)")
print("="*80)
kcp_codes_str = [str(c) for c in KCP_CODES]
qs_kcp = qs_filtered.filter(kode_uker__in=kcp_codes_str)
os_kcp_by_parent = {}
for row in qs_kcp.values('kode_uker').annotate(total_os=Sum('os')):
    kode_kcp = int(row['kode_uker'])
    os_value = float(row['total_os'] or 0)
    
    # Get parent KANCA
    if kode_kcp in UKER_MASTER:
        _, kode_kanca_induk = UKER_MASTER[kode_kcp]
        if kode_kanca_induk not in os_kcp_by_parent:
            os_kcp_by_parent[kode_kanca_induk] = 0
        os_kcp_by_parent[kode_kanca_induk] += os_value

# Print KCP grouped by parent
for kode_kanca in sorted(KANCA_CODES):
    kcp_total = os_kcp_by_parent.get(kode_kanca, 0)
    if kcp_total > 0:
        print(f"  KCP under KANCA {kode_kanca} ({KANCA_MASTER.get(kode_kanca, '?')}): {kcp_total:,.2f}")

# Compare
print("\n" + "="*80)
print("PERBANDINGAN HASIL")
print("="*80)

# Totals
total_konsol = sum(os_by_kanca_konsol.values())
total_kanca_only = sum(os_kanca_only.values())
total_kcp_only = sum(os_kcp_by_parent.values())

print(f"\nTOTAL RO Bandung:")
print(f"  KONSOL        : {total_konsol:>20,.2f}")
print(f"  KANCA ONLY    : {total_kanca_only:>20,.2f}")
print(f"  KCP ONLY      : {total_kcp_only:>20,.2f}")
print(f"  KANCA + KCP   : {(total_kanca_only + total_kcp_only):>20,.2f}")
print(f"  SELISIH       : {(total_konsol - (total_kanca_only + total_kcp_only)):>20,.2f}")

# Detail per KANCA dengan perbedaan
print("\n" + "="*80)
print("DETAIL PER KANCA (hanya yang ada perbedaan)")
print("="*80)

for kode_kanca in sorted(KANCA_CODES):
    nama_kanca = KANCA_MASTER.get(kode_kanca, f"KANCA {kode_kanca}")
    
    konsol_val = os_by_kanca_konsol.get(kode_kanca, 0)
    kanca_val = os_kanca_only.get(kode_kanca, 0)
    kcp_val = os_kcp_by_parent.get(kode_kanca, 0)
    
    expected = kanca_val + kcp_val
    diff = konsol_val - expected
    
    if abs(diff) > 0.01:  # Ada perbedaan
        print(f"\n{nama_kanca} ({kode_kanca}):")
        print(f"  KONSOL      : {konsol_val:>15,.2f}")
        print(f"  KANCA       : {kanca_val:>15,.2f}")
        print(f"  KCP         : {kcp_val:>15,.2f}")
        print(f"  KANCA + KCP : {expected:>15,.2f}")
        print(f"  SELISIH     : {diff:>15,.2f} {'✓' if abs(diff) < 0.01 else '✗'}")

print("\n" + "="*80)
print("SELESAI")
print("="*80)
