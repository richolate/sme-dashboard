"""
Check if 286 is in KCP_CODES or KANCA_CODES
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from dashboard.formulas.uker_mapping import UKER_MASTER, KANCA_CODES, KCP_CODES, KANCA_MASTER

print("Checking classification of code 286...")
print("=" * 80)

kode = 286

print(f"\nKode {kode}:")
if kode in UKER_MASTER:
    nama, induk = UKER_MASTER[kode]
    print(f"  Nama: {nama}")
    print(f"  Induk: {induk}")
    print(f"  In KANCA_CODES: {kode in KANCA_CODES}")
    print(f"  In KCP_CODES: {kode in KCP_CODES}")
else:
    print(f"  NOT in UKER_MASTER!")

print(f"\nIs 286 in KANCA_MASTER? {286 in KANCA_MASTER}")
if 286 in KANCA_MASTER:
    print(f"  KANCA name: {KANCA_MASTER[286]}")

print(f"\nKANCA_CODES (first 10): {KANCA_CODES[:10]}")
print(f"\nKCP_CODES containing 286: {[k for k in KCP_CODES if k == 286]}")

# Check naming logic
if kode in UKER_MASTER:
    nama, induk = UKER_MASTER[kode]
    starts_with_kcp = nama.upper().startswith("KCP")
    starts_with_kc = nama.upper().startswith("KC")
    print(f"\nNaming analysis:")
    print(f"  Name: {nama}")
    print(f"  Starts with 'KCP': {starts_with_kcp}")
    print(f"  Starts with 'KC': {starts_with_kc}")
    print(f"  kode_uker != kode_kanca: {kode != induk}")
    print(f"  Should be in KCP_CODES: {kode != induk and starts_with_kcp}")
