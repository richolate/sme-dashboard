# Field Type Revisions - LW321 Model

## Tanggal: 24 Desember 2025

## Latar Belakang
Setelah pengecekan database, ditemukan beberapa field yang memiliki tipe data tidak sesuai dengan isi data yang sebenarnya. Misalnya field tanggal yang berisi nilai kosong, 0, atau format yang tidak konsisten. Oleh karena itu dilakukan revisi tipe data untuk beberapa field.

## Perubahan Field Types

### 1. VARCHAR Length Optimization
Field yang diperpendek untuk efisiensi:

| Field | Sebelum | Sesudah | Alasan |
|-------|---------|---------|--------|
| **periode** | VARCHAR(30) | VARCHAR(20) | Cukup untuk format tanggal |
| **kanca** | VARCHAR(150) | VARCHAR(50) | Nama kanca tidak sepanjang itu |
| **kode_uker** | VARCHAR(50) | VARCHAR(10) | Kode uker singkat |
| **uker** | VARCHAR(150) | VARCHAR(50) | Nama uker tidak sepanjang itu |
| **ln_type** | VARCHAR(50) | VARCHAR(10) | Tipe loan singkat |
| **nama_debitur** | VARCHAR(200) | VARCHAR(50) | Optimisasi panjang nama |
| **flag_restruk** | VARCHAR(50) | VARCHAR(10) | Flag singkat |
| **kol_adk** | VARCHAR(50) | VARCHAR(10) | Kode kolektibilitas singkat |
| **pn_rm** | VARCHAR(150) | VARCHAR(20) | PN RM singkat |
| **nama_rm** | VARCHAR(150) | VARCHAR(50) | Nama RM tidak sepanjang itu |

### 2. Date Fields → VARCHAR
Field tanggal yang diubah menjadi VARCHAR karena data tidak konsisten (ada yang kosong, 0, atau format tanggal):

| Field | Sebelum | Sesudah | Alasan |
|-------|---------|---------|--------|
| **next_pmt_date** | DateField | VARCHAR(20) | Data ada yang kosong/0 |
| **next_int_pmt_date** | DateField | VARCHAR(20) | Data ada yang kosong/0 |
| **tgl_menunggak** | DateField | VARCHAR(20) | Data ada yang kosong/0 |
| **tgl_realisasi** | DateField | VARCHAR(20) | Data ada yang kosong/0 |
| **tgl_jatuh_tempo** | DateField | VARCHAR(20) | Data ada yang kosong/0 |

### 3. Numeric Type Changes

#### RATE (Decimal Precision)
- **Sebelum**: DecimalField(max_digits=7, decimal_places=4)
- **Sesudah**: DecimalField(max_digits=5, decimal_places=2)
- **Alasan**: Rate harusnya 10.99 bukan 10.9900 (2 desimal cukup)
- **Contoh**: 10.99, 12.50, 8.75

#### JANGKA WAKTU (Integer → VARCHAR)
- **Sebelum**: IntegerField
- **Sesudah**: VARCHAR(10)
- **Alasan**: Data berisi format seperti "106M" (bukan pure integer)
- **Contoh**: 106M, 24M, 36M

### 4. New Fields (dari migration sebelumnya)
| Field | Type | Keterangan | Status |
|-------|------|------------|--------|
| **nasabah** | DecimalField(18,2) | Jumlah nasabah | Perlu dicek data |
| **dub_nasabah** | BooleanField | Flag DUB NASABAH | Perlu dicek data |

## Files Modified

### 1. dashboard/models.py
- Updated field definitions dengan tipe data baru
- Semua date fields sekarang VARCHAR(20) dengan null=True, blank=True
- Rate precision diubah dari (7,4) ke (5,2)

### 2. data_management/utils.py
- **DATE_FIELDS** dikosongkan (semua tanggal sudah jadi varchar)
- **INTEGER_FIELDS** dikosongkan (jangka_waktu sudah jadi varchar)
- DECIMAL_FIELDS tetap untuk: plafon, rate, tunggakan_pokok, tunggakan_bunga, tunggakan_pinalti, os, nasabah
- BOOLEAN_FIELDS untuk: dub_nasabah

### 3. dashboard/admin.py
- Removed `date_hierarchy = 'next_pmt_date'` karena field sudah bukan DateField

### 4. Migrations
- **0011_alter_field_types.py**: Migration untuk semua perubahan tipe field

## Impact Analysis

### Positive Impact ✅
1. **Data Consistency**: Field types sekarang match dengan actual data
2. **Storage Optimization**: VARCHAR fields yang diperpendek menghemat space
3. **Flexibility**: VARCHAR untuk tanggal lebih flexible untuk handle data tidak konsisten
4. **Precision**: RATE dengan 2 decimal places lebih sesuai dengan kebutuhan bisnis

### Considerations ⚠️
1. **Date Filtering**: Field tanggal sekarang VARCHAR, jadi filtering/sorting by date perlu conversion
2. **Validation**: Perlu add validation di upload process untuk ensure date format consistency
3. **Existing Data**: Data existing sudah di-migrate, perlu verify data integrity

## Testing Checklist

- [x] Create migration successfully
- [x] Run migration successfully
- [ ] Test file upload dengan data baru
- [ ] Verify NASABAH field terisi dengan benar
- [ ] Verify DUB NASABAH field terisi dengan benar (TRUE/FALSE)
- [ ] Verify RATE field shows 2 decimal places (10.99 not 10.9900)
- [ ] Verify tanggal fields accept various formats (date string, empty, 0)
- [ ] Verify JANGKA WAKTU accepts format like "106M"

## Next Steps

1. **Upload Test File**
   - Create Excel file dengan data baru
   - Test all new field types
   - Verify NASABAH dan DUB NASABAH terisi

2. **Data Verification**
   - Check database untuk ensure all fields populated correctly
   - Verify RATE precision (should be 10.99 not 10.9900)
   - Verify tanggal fields handle empty/0 values

3. **Documentation Update**
   - Update upload template dengan format yang benar
   - Document expected formats untuk each field

## Database Schema Summary (After Changes)

```python
# LW321 Model - 35 fields total (33 data columns + 2 timestamps)

# Text Fields (VARCHAR)
periode = VARCHAR(20) - required
kanca = VARCHAR(50)
kode_uker = VARCHAR(10)
uker = VARCHAR(50)
ln_type = VARCHAR(10)
nomor_rekening = VARCHAR(50) - required, indexed
nama_debitur = VARCHAR(50)
flag_restruk = VARCHAR(10)
cif_no = VARCHAR(50)
kol_adk = VARCHAR(10)
pn_rm = VARCHAR(20)
nama_rm = VARCHAR(50)
code = VARCHAR(50)
description = VARCHAR(255)
jangka_waktu = VARCHAR(10) - format: "106M"

# Date as VARCHAR (flexible for empty/0/date string)
next_pmt_date = VARCHAR(20)
next_int_pmt_date = VARCHAR(20)
tgl_menunggak = VARCHAR(20)
tgl_realisasi = VARCHAR(20)
tgl_jatuh_tempo = VARCHAR(20)

# Kolektibilitas Fields (VARCHAR 50)
kolektibilitas_lancar = VARCHAR(50)
kolektibilitas_dpk = VARCHAR(50)
kolektibilitas_kurang_lancar = VARCHAR(50)
kolektibilitas_diragukan = VARCHAR(50)
kolektibilitas_macet = VARCHAR(50)

# Decimal Fields (18,2)
plafon = DECIMAL(18,2)
tunggakan_pokok = DECIMAL(18,2)
tunggakan_bunga = DECIMAL(18,2)
tunggakan_pinalti = DECIMAL(18,2)
os = DECIMAL(18,2)
nasabah = DECIMAL(18,2)

# Rate (5,2) - 2 decimal places
rate = DECIMAL(5,2) - example: 10.99, 12.50

# Boolean
dub_nasabah = BOOLEAN - TRUE/FALSE

# Timestamps (auto-managed)
created_at = TIMESTAMP
updated_at = TIMESTAMP
```

## Conclusion

Revisi field types berhasil dilakukan untuk meningkatkan data consistency dan storage efficiency. Semua perubahan sudah di-apply ke database melalui migration. Langkah selanjutnya adalah testing dengan upload file baru untuk memastikan semua field type changes bekerja dengan baik.
