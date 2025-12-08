"""
Test script untuk UKER Mapping
Jalankan dengan: python -m dashboard.formulas.test_uker_mapping
"""

from .uker_mapping import (
    KANCA_MASTER,
    UKER_MASTER,
    KANCA_CODES,
    KCP_CODES,
    is_kanca,
    is_kcp,
    get_kanca_induk,
    get_uker_name,
    get_kcp_by_kanca,
    get_uker_type,
    get_kanca_with_kcp_grouped,
)


def test_uker_mapping():
    print("=" * 70)
    print("TEST UKER MAPPING")
    print("=" * 70)
    
    # 1. Test KANCA_MASTER
    print(f"\n[1] Total KANCA: {len(KANCA_MASTER)}")
    print("    Contoh KANCA:")
    for i, (kode, nama) in enumerate(list(KANCA_MASTER.items())[:5]):
        print(f"       - {kode}: {nama}")
    
    # 2. Test UKER_MASTER
    print(f"\n[2] Total UKER (KANCA + KCP): {len(UKER_MASTER)}")
    
    # 3. Test KANCA_CODES dan KCP_CODES
    print(f"\n[3] KANCA_CODES: {len(KANCA_CODES)} items")
    print(f"    KCP_CODES: {len(KCP_CODES)} items")
    
    # 4. Test is_kanca dan is_kcp
    print("\n[4] Test is_kanca() dan is_kcp():")
    test_codes = [5, 675, 25, 1345, 100, 1337]
    for code in test_codes:
        nama = get_uker_name(code) or "Unknown"
        print(f"    - {code} ({nama}): is_kanca={is_kanca(code)}, is_kcp={is_kcp(code)}")
    
    # 5. Test get_kanca_induk
    print("\n[5] Test get_kanca_induk():")
    test_kcp = [675, 1345, 1337, 2162]
    for code in test_kcp:
        induk = get_kanca_induk(code)
        nama_kcp = get_uker_name(code)
        nama_induk = KANCA_MASTER.get(induk, "Unknown")
        print(f"    - {code} ({nama_kcp}) → Induk: {induk} ({nama_induk})")
    
    # 6. Test get_kcp_by_kanca
    print("\n[6] Test get_kcp_by_kanca():")
    test_kanca = [5, 100, 401]
    for kode_kanca in test_kanca:
        nama_kanca = KANCA_MASTER.get(kode_kanca)
        kcp_list = get_kcp_by_kanca(kode_kanca)
        print(f"    {kode_kanca} ({nama_kanca}):")
        if kcp_list:
            for kode_kcp, nama_kcp in kcp_list:
                print(f"       └─ {kode_kcp}: {nama_kcp}")
        else:
            print(f"       └─ (tidak ada KCP)")
    
    # 7. Test get_uker_type
    print("\n[7] Test get_uker_type():")
    test_all = [5, 675, 1337, 9999]
    for code in test_all:
        tipe = get_uker_type(code)
        nama = get_uker_name(code) or "Not Found"
        print(f"    - {code} ({nama}): {tipe}")
    
    # 8. Summary KANCA dengan KCP
    print("\n[8] Summary KANCA dengan KCP:")
    grouped = get_kanca_with_kcp_grouped()
    kanca_with_kcp = sum(1 for k, v in grouped.items() if len(v['kcp_list']) > 0)
    kanca_without_kcp = sum(1 for k, v in grouped.items() if len(v['kcp_list']) == 0)
    print(f"    - KANCA dengan KCP: {kanca_with_kcp}")
    print(f"    - KANCA tanpa KCP: {kanca_without_kcp}")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETED!")
    print("=" * 70)


if __name__ == "__main__":
    test_uker_mapping()
