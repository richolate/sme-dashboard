"""
Quick test to verify KCP table building works with correct data types
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from dashboard.formulas.uker_mapping import (
    KANCA_MASTER,
    KANCA_CODES,
    get_kcp_by_kanca
)

print("=" * 80)
print("Testing KCP Data Structure Fix")
print("=" * 80)

# Test 1: Verify KANCA_CODES are integers
print("\n1. Testing KANCA_CODES data types:")
print(f"   Total KANCA: {len(KANCA_CODES)}")
print(f"   Sample KANCA codes: {KANCA_CODES[:5]}")
print(f"   All are integers: {all(isinstance(k, int) for k in KANCA_CODES)}")

# Test 2: Verify get_kcp_by_kanca returns integers
print("\n2. Testing get_kcp_by_kanca() function:")
for kode_kanca in KANCA_CODES[:3]:  # Test first 3 KANCA
    kcp_list = get_kcp_by_kanca(kode_kanca)
    print(f"\n   KANCA {kode_kanca} ({KANCA_MASTER[kode_kanca]}):")
    print(f"   - Total KCP: {len(kcp_list)}")
    if kcp_list:
        kcp_code, kcp_name = kcp_list[0]
        print(f"   - Sample KCP: {kcp_code} ({kcp_name})")
        print(f"   - KCP code is int: {isinstance(kcp_code, int)}")

# Test 3: Simulate the sorting logic
print("\n3. Testing sorting logic (like in build_kcp_only_table):")
kcp_list = []
for kode_kanca in KANCA_CODES[:3]:  # Test first 3 KANCA
    kcp_data = get_kcp_by_kanca(kode_kanca)
    for kcp_code, kcp_name in kcp_data:
        kcp_list.append({
            'kode_kanca': kode_kanca,
            'kcp_code': kcp_code,
            'kanca_name': KANCA_MASTER.get(kode_kanca)
        })

print(f"   Total KCP collected: {len(kcp_list)}")

# This should NOT raise TypeError anymore
try:
    kcp_list.sort(key=lambda x: (x['kode_kanca'], x['kcp_code']))
    print("   ✅ Sorting successful! No TypeError.")
    print(f"   First 3 sorted items:")
    for item in kcp_list[:3]:
        print(f"      - KANCA {item['kode_kanca']}, KCP {item['kcp_code']}")
except TypeError as e:
    print(f"   ❌ Sorting failed with TypeError: {e}")

print("\n" + "=" * 80)
print("Test completed!")
print("=" * 80)
