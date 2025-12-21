"""
Manual Test Guide for Date Filter Persistence Feature

Test ini untuk memverifikasi bahwa filter tanggal tetap tersimpan
saat user berpindah antar halaman dalam dashboard.
"""

print("=" * 80)
print("MANUAL TEST GUIDE - DATE FILTER PERSISTENCE")
print("=" * 80)

print("\n📋 TESTING STEPS:")
print("-" * 80)

print("\n✅ TEST 1: Save Date to localStorage")
print("   1. Buka browser: http://127.0.0.1:8000/page/small-os/")
print("   2. Pilih tanggal: 30 November 2025 (30/11/2025)")
print("   3. Klik tombol 'Terapkan'")
print("   4. Buka Developer Tools (F12) -> Console")
print("   5. Run: localStorage.getItem('dashboard_selected_date')")
print("   6. EXPECTED: '2025-11-30'")
print("   7. Verify URL berubah ke: ...?selected_date=2025-11-30")

print("\n✅ TEST 2: Navigate to Another Page (DPK SMALL)")
print("   1. Dari halaman OS SMALL (dengan tanggal 30 Nov 2025)")
print("   2. Klik menu sidebar 'DPK SMALL'")
print("   3. EXPECTED: URL berubah ke /page/small-dpk/?selected_date=2025-11-30")
print("   4. Verify halaman DPK menampilkan data untuk tanggal 30 Nov 2025")
print("   5. Verify input tanggal di halaman DPK terisi: 2025-11-30")

print("\n✅ TEST 3: Navigate to Another Page (NPL SMALL)")
print("   1. Dari halaman DPK SMALL (dengan tanggal 30 Nov 2025)")
print("   2. Klik menu sidebar 'NPL SMALL'")
print("   3. EXPECTED: URL berubah ke /page/small-npl/?selected_date=2025-11-30")
print("   4. Verify halaman NPL menampilkan data untuk tanggal 30 Nov 2025")
print("   5. Verify input tanggal di halaman NPL terisi: 2025-11-30")

print("\n✅ TEST 4: Navigate to Another Page (LR SMALL)")
print("   1. Dari halaman NPL SMALL (dengan tanggal 30 Nov 2025)")
print("   2. Klik menu sidebar 'LR SMALL'")
print("   3. EXPECTED: URL berubah ke /page/small-lr/?selected_date=2025-11-30")
print("   4. Verify halaman LR menampilkan data untuk tanggal 30 Nov 2025")
print("   5. Verify input tanggal di halaman LR terisi: 2025-11-30")

print("\n✅ TEST 5: Navigate to Another Page (LAR SMALL)")
print("   1. Dari halaman LR SMALL (dengan tanggal 30 Nov 2025)")
print("   2. Klik menu sidebar 'LAR SMALL'")
print("   3. EXPECTED: URL berubah ke /page/small-lar/?selected_date=2025-11-30")
print("   4. Verify halaman LAR menampilkan data untuk tanggal 30 Nov 2025")
print("   5. Verify input tanggal di halaman LAR terisi: 2025-11-30")

print("\n✅ TEST 6: Refresh Browser")
print("   1. Dari halaman apapun dengan tanggal terpilih")
print("   2. Tekan F5 atau Ctrl+R untuk refresh")
print("   3. EXPECTED: Halaman reload dengan tanggal yang sama")
print("   4. Verify data dan input tanggal masih sama")

print("\n✅ TEST 7: New Tab with Same Domain")
print("   1. Dengan tanggal 30 Nov 2025 masih di localStorage")
print("   2. Buka tab baru di browser yang sama")
print("   3. Akses: http://127.0.0.1:8000/page/small-os/")
print("   4. EXPECTED: Input tanggal otomatis terisi 2025-11-30")
print("   5. (Note: URL mungkin belum ada parameter, tapi input terisi)")

print("\n✅ TEST 8: Change Date Multiple Times")
print("   1. Buka halaman OS SMALL dengan tanggal 30 Nov 2025")
print("   2. Ubah tanggal ke: 31 Desember 2024")
print("   3. Klik 'Terapkan'")
print("   4. Navigate ke DPK SMALL")
print("   5. EXPECTED: DPK tampil dengan tanggal 31 Des 2024")
print("   6. Verify localStorage: localStorage.getItem('dashboard_selected_date')")
print("   7. EXPECTED: '2024-12-31'")

print("\n✅ TEST 9: Clear localStorage and Reset")
print("   1. Buka Developer Tools -> Console")
print("   2. Run: localStorage.removeItem('dashboard_selected_date')")
print("   3. Refresh halaman")
print("   4. EXPECTED: Tanggal kembali ke default server (latest date)")
print("   5. Verify input tanggal menampilkan tanggal default")

print("\n✅ TEST 10: JavaScript API Testing")
print("   1. Buka Developer Tools -> Console")
print("   2. Run: window.dashboardDateFilter.getSelectedDate()")
print("   3. EXPECTED: Return tanggal yang tersimpan (e.g., '2025-11-30')")
print("   4. Run: window.dashboardDateFilter.saveSelectedDate('2025-12-25')")
print("   5. Run: window.dashboardDateFilter.getSelectedDate()")
print("   6. EXPECTED: '2025-12-25'")
print("   7. Run: window.dashboardDateFilter.addDateToUrl('/page/small-npl/')")
print("   8. EXPECTED: '/page/small-npl/?selected_date=2025-12-25'")

print("\n" + "=" * 80)
print("🔧 BROWSER DEVELOPER TOOLS COMMANDS")
print("=" * 80)

print("\n// Check current selected date")
print("window.dashboardDateFilter.getSelectedDate()")

print("\n// Check localStorage directly")
print("localStorage.getItem('dashboard_selected_date')")

print("\n// Manually set date")
print("window.dashboardDateFilter.saveSelectedDate('2025-11-30')")

print("\n// Test URL generation")
print("window.dashboardDateFilter.addDateToUrl('/page/small-os/')")

print("\n// Clear date")
print("localStorage.removeItem('dashboard_selected_date')")

print("\n// Update all navigation links")
print("window.dashboardDateFilter.updateNavigationLinks()")

print("\n" + "=" * 80)
print("✅ EXPECTED BEHAVIOR SUMMARY")
print("=" * 80)

print("\n1. ✓ Tanggal tersimpan ke localStorage saat user klik 'Terapkan'")
print("2. ✓ URL otomatis include parameter ?selected_date=YYYY-MM-DD")
print("3. ✓ Tanggal persisten saat navigate antar menu")
print("4. ✓ Input tanggal auto-populate dari localStorage")
print("5. ✓ Tanggal tetap ada setelah refresh browser")
print("6. ✓ Tanggal shared antar tabs di browser yang sama")
print("7. ✓ Clear localStorage reset ke default server")
print("8. ✓ API JavaScript berfungsi dengan baik")

print("\n" + "=" * 80)
print("🚨 COMMON ISSUES & SOLUTIONS")
print("=" * 80)

print("\n❌ Issue: Link tidak dapat parameter tanggal")
print("   Solution: Verify link memiliki class 'nav-link'")
print("   Solution: Check URL pattern (/page/ atau /dashboard/)")

print("\n❌ Issue: localStorage tidak save")
print("   Solution: Check browser console untuk JavaScript errors")
print("   Solution: Verify browser allows localStorage (not in incognito/private)")

print("\n❌ Issue: Tanggal tidak muncul di input")
print("   Solution: Verify input memiliki id='selectedDateInput'")
print("   Solution: Check form memiliki id='dateFilterForm'")

print("\n" + "=" * 80)
print("📊 SUCCESS CRITERIA")
print("=" * 80)

print("\n✅ ALL TESTS MUST PASS:")
print("   • Date saves to localStorage on form submit")
print("   • Date persists when navigating between pages")
print("   • URL includes selected_date parameter")
print("   • Date input auto-populates from localStorage")
print("   • Date survives browser refresh")
print("   • JavaScript API functions correctly")
print("   • Clear localStorage resets to default")

print("\n" + "=" * 80)
print("🎯 START TESTING NOW!")
print("=" * 80)
print("\n1. Start Django dev server: python manage.py runserver")
print("2. Open browser: http://127.0.0.1:8000/page/small-os/")
print("3. Follow test steps above")
print("4. Report any issues found")
print("\n" + "=" * 80)
