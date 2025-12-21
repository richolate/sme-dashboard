# Date Filter Persistence Feature

## Overview

Fitur ini memungkinkan filter tanggal yang dipilih user tetap **persisten** (tersimpan) ketika berpindah antar halaman/menu dalam dashboard.

## Cara Kerja

### 1. **Penyimpanan Tanggal**
- Ketika user memilih tanggal dan klik "Terapkan", tanggal tersebut disimpan ke **localStorage** browser
- localStorage key: `dashboard_selected_date`
- Format tanggal: `YYYY-MM-DD` (format HTML5 date input)

### 2. **Persistence Saat Navigasi**
Ketika user klik menu lain, sistem otomatis:
- Mengambil tanggal dari localStorage
- Menambahkan parameter `?selected_date=YYYY-MM-DD` ke URL tujuan
- Halaman baru akan langsung menampilkan data sesuai tanggal yang dipilih

### 3. **Prioritas Sumber Tanggal**
Sistem menggunakan prioritas berikut untuk menentukan tanggal yang digunakan:

**Priority 1:** Query parameter URL (`?selected_date=2025-11-30`)
- Jika ada di URL, gunakan ini dan simpan ke localStorage

**Priority 2:** localStorage browser
- Jika tidak ada di URL, ambil dari localStorage

**Priority 3:** Default server
- Jika kedua sumber di atas kosong, gunakan default dari server (latest date)

## Implementasi Teknis

### File yang Dimodifikasi

#### 1. `templates/base.html`
Menambahkan JavaScript function global untuk date persistence:

```javascript
// Key functions:
- getSelectedDate()           // Ambil tanggal dari URL/localStorage
- saveSelectedDate(date)      // Simpan tanggal ke localStorage
- addDateToUrl(url)           // Tambahkan parameter tanggal ke URL
- updateNavigationLinks()     // Update semua link menu dengan tanggal
- interceptLinkClicks()       // Intercept klik menu untuk inject tanggal
- monitorDateInput()          // Monitor perubahan input tanggal
```

**Features:**
- ✅ Automatic URL parameter injection untuk semua link `/page/` dan `/dashboard/`
- ✅ Click interception pada navigation links
- ✅ localStorage synchronization
- ✅ Exposed global API: `window.dashboardDateFilter`

#### 2. `templates/dashboard/metric_page.html`
Menambahkan form submit handler untuk menyimpan tanggal:

```javascript
// Form submission handler
dateFilterForm.addEventListener('submit', function(e) {
    const selectedDate = dateInput.value;
    if (selectedDate) {
        localStorage.setItem('dashboard_selected_date', selectedDate);
    }
});
```

**Features:**
- ✅ Save tanggal ke localStorage saat form submit
- ✅ Auto-populate input jika localStorage ada nilai

## Contoh Penggunaan

### Skenario 1: User di Halaman OS SMALL
```
1. User buka: http://localhost:8000/page/small-os/
2. User pilih tanggal: 30 November 2025
3. User klik "Terapkan"
4. URL berubah: http://localhost:8000/page/small-os/?selected_date=2025-11-30
5. Tanggal disimpan ke localStorage
```

### Skenario 2: User Pindah ke Halaman DPK SMALL
```
1. User klik menu "DPK SMALL" di sidebar
2. JavaScript otomatis inject parameter tanggal
3. Browser navigasi ke: http://localhost:8000/page/small-dpk/?selected_date=2025-11-30
4. Halaman DPK SMALL langsung tampil dengan tanggal 30 November 2025
5. Filter tanggal di halaman DPK sudah terisi: 30 November 2025
```

### Skenario 3: User Refresh Browser
```
1. User tekan F5 atau refresh browser
2. Tanggal masih ada di localStorage
3. Halaman reload dengan tanggal yang sama
4. Data tetap konsisten
```

### Skenario 4: User Buka Tab Baru
```
1. User buka tab baru di browser yang sama
2. localStorage masih ada (shared antar tab)
3. User buka halaman dashboard manapun
4. Tanggal otomatis terbawa dari localStorage
```

## JavaScript API

Sistem menyediakan global API untuk debugging atau custom integration:

```javascript
// Get currently selected date
const date = window.dashboardDateFilter.getSelectedDate();
console.log('Selected date:', date); // "2025-11-30"

// Manually save a date
window.dashboardDateFilter.saveSelectedDate('2025-12-31');

// Add date parameter to any URL
const url = '/page/small-npl/';
const newUrl = window.dashboardDateFilter.addDateToUrl(url);
console.log(newUrl); // "/page/small-npl/?selected_date=2025-11-30"

// Refresh all navigation links
window.dashboardDateFilter.updateNavigationLinks();
```

## Browser Compatibility

Fitur ini menggunakan:
- ✅ **localStorage API** - Supported di semua modern browsers (IE 8+)
- ✅ **URLSearchParams API** - Supported di semua modern browsers
- ✅ **addEventListener** - Standard DOM API

**Minimum Requirements:**
- Chrome 4+
- Firefox 3.5+
- Safari 4+
- Edge (all versions)
- IE 11+ (dengan polyfill URLSearchParams jika perlu)

## Keamanan & Privacy

### Data Storage
- **Lokasi:** localStorage browser (client-side only)
- **Scope:** Per domain/origin
- **Persistence:** Permanent sampai user clear browser data
- **Size:** ~10 bytes (format: "YYYY-MM-DD")

### Privacy Considerations
- ❌ **TIDAK** dikirim ke server secara otomatis
- ✅ **Hanya** tersimpan di browser user
- ✅ **Tidak** melintasi domain (XSS protection)
- ✅ **User kontrol penuh** via browser settings (clear data)

## Troubleshooting

### Issue: Tanggal tidak tersimpan saat pindah menu
**Solution:**
1. Cek console browser untuk JavaScript errors
2. Verify localStorage tidak disabled:
   ```javascript
   console.log(localStorage.getItem('dashboard_selected_date'));
   ```
3. Clear localStorage dan coba lagi:
   ```javascript
   localStorage.clear();
   ```

### Issue: Link tidak mendapat parameter tanggal
**Solution:**
1. Cek apakah link termasuk `.nav-link` class
2. Verify URL pattern (`/page/` atau `/dashboard/`)
3. Check console untuk intercepted clicks

### Issue: Form submit tidak save tanggal
**Solution:**
1. Cek apakah form memiliki `id="dateFilterForm"`
2. Verify input memiliki `id="selectedDateInput"`
3. Check JavaScript console untuk errors

## Testing

### Manual Testing Steps

1. **Test Basic Functionality:**
   ```
   - Buka halaman OS SMALL
   - Pilih tanggal berbeda dari default
   - Klik "Terapkan"
   - Verify URL berubah dengan parameter selected_date
   - Verify tanggal tersimpan di localStorage
   ```

2. **Test Navigation:**
   ```
   - Dari halaman OS SMALL (dengan tanggal terpilih)
   - Klik menu "NPL SMALL"
   - Verify halaman NPL SMALL tampil dengan tanggal yang sama
   - Verify input tanggal di NPL SMALL sudah terisi
   ```

3. **Test Persistence:**
   ```
   - Pilih tanggal di halaman manapun
   - Close browser tab
   - Buka tab baru, akses dashboard
   - Verify tanggal masih persisten
   ```

4. **Test Clear:**
   ```
   - Clear browser data (localStorage)
   - Reload halaman
   - Verify kembali ke tanggal default server
   ```

### Browser Console Testing

```javascript
// Check current date
console.log(window.dashboardDateFilter.getSelectedDate());

// Test save
window.dashboardDateFilter.saveSelectedDate('2025-12-25');

// Test URL generation
console.log(window.dashboardDateFilter.addDateToUrl('/page/small-lar/'));

// Check localStorage directly
console.log(localStorage.getItem('dashboard_selected_date'));

// Clear date
localStorage.removeItem('dashboard_selected_date');
```

## Future Enhancements

Possible improvements:
- [ ] Add date range picker (from-to dates)
- [ ] Sync date across multiple browser tabs in real-time (BroadcastChannel API)
- [ ] Add "Reset to Default" button
- [ ] Store multiple date presets
- [ ] Export/Import date selections
- [ ] Date history (last 5 selected dates)

## Related Files

- `templates/base.html` - Core persistence logic
- `templates/dashboard/metric_page.html` - Form submission handler
- `dashboard/views.py` - Server-side date handling
- `dashboard/formulas/metric_handlers.py` - Date parameter processing

## Maintenance Notes

**When adding new pages:**
- ✅ No code changes needed! Automatic for all `/page/` and `/dashboard/` URLs
- ✅ Just ensure page accepts `?selected_date=YYYY-MM-DD` parameter
- ✅ Use same date input structure as metric_page.html

**When modifying navigation:**
- ✅ Keep `.nav-link` class on menu items
- ✅ Ensure href points to proper URL pattern
- ✅ Date injection happens automatically

## Version History

**v1.0 (December 2025)**
- Initial implementation
- localStorage-based persistence
- Automatic link injection
- Form submission handler
- Global JavaScript API

---

**Contact:** Dashboard Development Team
**Last Updated:** December 22, 2025
