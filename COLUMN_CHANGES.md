# Revisi Kolom dan Fungsi Upload Data# Perubahan Struktur Kolom LW321



## Tanggal: 23 Desember 2025## Tanggal: 10 Desember 2025



## Summary Perubahan### ❌ Kolom yang Dihapus (9 kolom)



### 1. Perubahan Struktur Kolom1. `pn_pengelola_1` - PN PENGELOLA 1

2. `pn_pemrakarsa` - PN PEMRAKARSA

#### COLUMN_FIELD_MAP Terbaru (31 kolom):3. `pn_referral` - PN REFERRAL

```4. `pn_restruk` - PN RESTRUK

1.  PERIODE → periode5. `pn_pengelola_2` - PN PENGELOLA 2

2.  KANCA → kanca6. `pn_pemutus` - PN PEMUTUS

3.  KODE UKER → kode_uker7. `pn_crm` - PN CRM

4.  UKER → uker8. `pn_rm_referral_naik_segmentasi` - PN RM REFERRAL NAIK SEGMENTASI

5.  LN TYPE → ln_type9. `pn_rm_crr` - PN RM CRR

6.  NOMOR REKENING → nomor_rekening

7.  NAMA DEBITUR → nama_debitur### ✅ Kolom yang Ditambahkan (1 kolom)

8.  PLAFON → plafon

9.  NEXT PMT DATE → next_pmt_date1. `nama_rm` - NAMA RM

10. NEXT INT PMT DATE → next_int_pmt_date

11. RATE → rate### 📋 Struktur Kolom Final (30 kolom)

12. TGL MENUNGGAK → tgl_menunggak

13. TGL REALISASI → tgl_realisasi1. PERIODE

14. TGL JATUH TEMPO → tgl_jatuh_tempo2. KANCA

15. JANGKA WAKTU → jangka_waktu3. KODE UKER

16. FLAG RESTRUK → flag_restruk4. UKER

17. CIFNO → cif_no5. LN TYPE

18. KOLEKTIBILITAS LANCAR → kolektibilitas_lancar6. NOMOR REKENING

19. KOLEKTIBILITAS DPK → kolektibilitas_dpk7. NAMA DEBITUR

20. KOLEKTIBILITAS KURANG LANCAR → kolektibilitas_kurang_lancar8. PLAFON

21. KOLEKTIBILITAS DIRAGUKAN → kolektibilitas_diragukan9. NEXT PMT DATE

22. KOLEKTIBILITAS MACET → kolektibilitas_macet10. NEXT INT PMT DATE

23. TUNGGAKAN POKOK → tunggakan_pokok11. RATE

24. TUNGGAKAN BUNGA → tunggakan_bunga12. TGL MENUNGGAK

25. TUNGGAKAN PINALTI → tunggakan_pinalti13. TGL REALISASI

26. CODE → code14. TGL JATUH TEMPO

27. DESCRIPTION → description15. JANGKA WAKTU

28. KOL_ADK → kol_adk16. FLAG RESTRUK

29. PN RM → pn_rm (RENAMED dari pn_pengelola_singlepn)17. CIFNO

30. NAMA RM → nama_rm18. KOLEKTIBILITAS LANCAR

31. OS → os (KOLOM BARU)19. KOLEKTIBILITAS DPK

```20. KOLEKTIBILITAS KURANG LANCAR

21. KOLEKTIBILITAS DIRAGUKAN

### 2. Rumus Perhitungan Baru22. KOLEKTIBILITAS MACET

23. TUNGGAKAN POKOK

**DPK/SML:** `SUM(OS) WHERE KOL_ADK = '2'`  24. TUNGGAKAN BUNGA

**NPL:** `SUM(OS) WHERE KOL_ADK IN ('3', '4', '5')`  25. TUNGGAKAN PINALTI

26. CODE

### 3. Fitur Upload Baru27. DESCRIPTION

28. KOL_ADK

✅ **Preview Modal** - Validasi 10 sample data sebelum upload  29. PN PENGELOLA SINGLEPN

✅ **Color Coding** - Hijau (valid), Merah (missing)  30. **NAMA RM** ← Kolom baru

✅ **Auto TRIM** - Semua string di-trim otomatis  

✅ **Statistik Informatif** - Record count, customers, ukers per tanggal  ---



## Testing Required## File yang Diubah



1. Upload file dengan kolom OS### 1. `dashboard/models.py`

2. Verify DPK = SUM(OS WHERE KOL_ADK='2')- Hapus 9 field `pn_*` 

3. Verify NPL = SUM(OS WHERE KOL_ADK IN ('3','4','5'))- Tambah field `nama_rm`

4. Test preview modal functionality

5. Check TRIM working### 2. `data_management/utils.py`

- Update `COLUMN_FIELD_MAP` 

**Status:** ✅ READY FOR TESTING- Hapus mapping 9 kolom PN lama

- Tambah mapping `'NAMA RM': 'nama_rm'`
- Update format nama kolom dengan spasi (KODE UKER, LN TYPE, dll)

### 3. Migration
- Created: `0007_remove_lw321_pn_crm_remove_lw321_pn_pemrakarsa_and_more.py`
- Status: FAKED (kolom sudah tidak ada di DB)

---

## Format File Excel/CSV yang Diperlukan

Pastikan file upload memiliki kolom dengan nama (CASE SENSITIVE):

```
PERIODE
KANCA
KODE UKER          ← dengan spasi
UKER
LN TYPE            ← dengan spasi
NOMOR REKENING     ← dengan spasi (18 digit, akan auto-pad dengan leading zeros)
NAMA DEBITUR       ← dengan spasi
PLAFON
NEXT PMT DATE      ← dengan spasi
NEXT INT PMT DATE  ← dengan spasi
RATE
TGL MENUNGGAK      ← dengan spasi
TGL REALISASI      ← dengan spasi
TGL JATUH TEMPO    ← dengan spasi
JANGKA WAKTU       ← dengan spasi
FLAG RESTRUK       ← dengan spasi
CIFNO
KOLEKTIBILITAS LANCAR      ← dengan spasi
KOLEKTIBILITAS DPK         ← dengan spasi
KOLEKTIBILITAS KURANG LANCAR  ← dengan spasi
KOLEKTIBILITAS DIRAGUKAN   ← dengan spasi
KOLEKTIBILITAS MACET       ← dengan spasi
TUNGGAKAN POKOK    ← dengan spasi
TUNGGAKAN BUNGA    ← dengan spasi
TUNGGAKAN PINALTI  ← dengan spasi
CODE
DESCRIPTION
KOL_ADK
PN PENGELOLA SINGLEPN  ← dengan spasi
NAMA RM               ← KOLOM BARU dengan spasi
```

---

## Backward Compatibility

⚠️ **WARNING:** File lama dengan 9 kolom PN tidak akan error, tapi kolom tersebut akan diabaikan.

✅ **RECOMMENDED:** Update template Excel dengan struktur kolom baru (30 kolom).

---

## ⚠️ Format Nomor Rekening (PENTING!)

### Format yang Benar
- **Tipe Data**: Text/String (bukan Number!)
- **Panjang**: 18 digit
- **Leading Zeros**: HARUS dipertahankan

### Contoh Nomor Rekening yang Benar:
```
000000050104667108  ← 18 digit dengan leading zeros
000000050105456106
000000050105111103
000000050105300100
000000050105302102
```

### ❌ Format yang SALAH:
```
50104667108         ← Leading zeros hilang
5.0104667108E+10    ← Format scientific notation
"50104667108"       ← Kurang dari 18 digit
```

### 💡 Tips Excel:
1. **Set kolom sebagai Text** sebelum paste data
   - Select kolom NOMOR REKENING
   - Format Cells → Text
   - Paste data nomor rekening

2. **Atau gunakan apostrophe** di depan nomor:
   ```
   '000000050104667108
   ```

3. **Check leading zeros** sebelum save file:
   - Pastikan nomor rekening masih 18 digit
   - Pastikan dimulai dengan '0' jika memang ada leading zeros

### Sistem Auto-Correction:
Sistem akan otomatis:
- Convert nomor rekening ke string
- Pad dengan leading zeros jika kurang dari 18 digit
- Remove decimal point jika ada (dari float)

**Contoh:**
- Input: `50104667108` → Output: `000000050104667108`
- Input: `5.0104667108E+10` → Output: `000000050104667108`

---

## Testing

### Upload Test File
1. Buat file Excel dengan 30 kolom sesuai struktur baru
2. Isi kolom `NAMA RM` dengan data test
3. Upload melalui: http://localhost:8000/data-management/upload/
4. Verify data masuk dengan benar

### Query Test
```python
from dashboard.models import LW321

# Test query kolom baru
data = LW321.objects.filter(nama_rm__isnull=False)
print(data.count())
print(data.first().nama_rm)
```

---

## Migration Commands

```powershell
# Generate migration
python manage.py makemigrations dashboard --noinput

# Apply migration (fake karena kolom sudah tidak ada)
python manage.py migrate dashboard 0007 --fake

# Verify schema
python manage.py dbshell
\d lw321
\q
```

---

Perubahan selesai! ✅
