"""
Check which UKERs are missing from KANCA_CODES and KCP_CODES
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from dashboard.formulas.uker_mapping import UKER_MASTER, KANCA_CODES, KCP_CODES

print("Checking UKER classification...")
print("=" * 80)

missing_ukers = []

for kode_uker, (nama, kode_kanca) in sorted(UKER_MASTER.items()):
    is_kanca = kode_uker in KANCA_CODES
    is_kcp = kode_uker in KCP_CODES
    is_neither = not is_kanca and not is_kcp
    
    if is_neither:
        missing_ukers.append((kode_uker, nama, kode_kanca))
        print(f"❌ MISSING: {kode_uker} - {nama} (induk: {kode_kanca})")

print(f"\n{'='*80}")
print(f"Total UKERs in UKER_MASTER: {len(UKER_MASTER)}")
print(f"UKERs in KANCA_CODES: {len(KANCA_CODES)}")
print(f"UKERs in KCP_CODES: {len(KCP_CODES)}")
print(f"UKERs MISSING from both: {len(missing_ukers)}")

if missing_ukers:
    print(f"\n{'='*80}")
    print("PROBLEM: These UKERs are not in KANCA or KCP lists!")
    print("\nMissing UKERs:")
    for kode, nama, induk in missing_ukers:
        # Check naming pattern
        prefix = nama.split()[0] if nama else "UNKNOWN"
        print(f"  {kode}: {nama} (induk: {induk}) - starts with '{prefix}'")
