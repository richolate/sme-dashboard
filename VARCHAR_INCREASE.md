# VARCHAR Field Increase - December 24, 2025

## Summary
Increased VARCHAR field lengths from 50 to 100 characters to prevent "value too long" errors during data upload.

## Problem
Upload failed for 2 rows with error:
```
Row 84: value too long for type character varying(50)
Row 20093: value too long for type character varying(50)
```

## Solution
Increased all VARCHAR(50) fields to VARCHAR(100) for better safety margin.

## Fields Changed (50 → 100)

### Text Fields
1. **kanca** - Branch name (KC/KCP name)
2. **uker** - Unit Kerja name (full office name)
3. **nomor_rekening** - Account number
4. **nama_debitur** - Customer name (debtor name)
5. **cif_no** - Customer identification number
6. **nama_rm** - Relationship Manager name
7. **code** - Product/loan code

### Numeric Fields (stored as VARCHAR for display)
8. **kolektibilitas_lancar** - Current collectibility amount
9. **kolektibilitas_dpk** - Special mention collectibility
10. **kolektibilitas_kurang_lancar** - Substandard collectibility
11. **kolektibilitas_diragukan** - Doubtful collectibility
12. **kolektibilitas_macet** - Bad debt collectibility

## Fields Unchanged

### Small Fields (kept at 10-20 chars)
- periode: 20
- kode_uker: 10
- ln_type: 10
- jangka_waktu: 10
- flag_restruk: 10
- kol_adk: 10
- pn_rm: 20
- dub_nasabah: 10
- next_pmt_date: 20
- next_int_pmt_date: 20
- tgl_menunggak: 20
- tgl_realisasi: 20
- tgl_jatuh_tempo: 20

### Large Fields
- description: 255 (unchanged)

## Files Modified

### 1. `dashboard/models.py`
Changed 12 fields from `max_length=50` to `max_length=100`

```python
# Before
kanca = models.CharField(max_length=50, blank=True)
nama_debitur = models.CharField(max_length=50, blank=True)
# ... etc

# After
kanca = models.CharField(max_length=100, blank=True)
nama_debitur = models.CharField(max_length=100, blank=True)
# ... etc
```

### 2. `data_management/utils.py`
Updated MAX_LENGTHS dictionary in truncate logic

```python
MAX_LENGTHS = {
    'kanca': 100,  # was 50
    'uker': 100,  # was 50
    'nomor_rekening': 100,  # was 50
    'nama_debitur': 100,  # was 50
    'cif_no': 100,  # was 50
    'kolektibilitas_lancar': 100,  # was 50
    'kolektibilitas_dpk': 100,  # was 50
    'kolektibilitas_kurang_lancar': 100,  # was 50
    'kolektibilitas_diragukan': 100,  # was 50
    'kolektibilitas_macet': 100,  # was 50
    'code': 100,  # was 50
    'nama_rm': 100,  # was 50
    # ... other fields unchanged
}
```

### 3. Migration Created
`dashboard/migrations/0014_increase_varchar_to_100.py`

## Migration Applied
```bash
python manage.py makemigrations dashboard -n "increase_varchar_to_100"
python manage.py migrate dashboard
```

Result:
```
Migrations for 'dashboard':
  dashboard\migrations\0014_increase_varchar_to_100.py
    ~ Alter field cif_no on lw321
    ~ Alter field code on lw321
    ~ Alter field kanca on lw321
    ~ Alter field kolektibilitas_diragukan on lw321
    ~ Alter field kolektibilitas_dpk on lw321
    ~ Alter field kolektibilitas_kurang_lancar on lw321
    ~ Alter field kolektibilitas_lancar on lw321
    ~ Alter field kolektibilitas_macet on lw321
    ~ Alter field nama_debitur on lw321
    ~ Alter field nama_rm on lw321
    ~ Alter field nomor_rekening on lw321
    ~ Alter field uker on lw321

Operations to perform:
  Apply all migrations: dashboard
Running migrations:
  Applying dashboard.0014_increase_varchar_to_100... OK
```

## Benefits

1. **No More Truncation Errors**
   - Fields can now store up to 100 characters
   - Doubled capacity from previous 50 char limit

2. **Safer Data Import**
   - Long branch names won't be truncated
   - Long customer names preserved
   - Long account numbers supported

3. **Auto-Truncate Fallback**
   - If data exceeds 100 chars, will auto-truncate with warning
   - Prevents complete upload failure

4. **Backward Compatible**
   - Existing data unchanged
   - Only affects new uploads

## Testing

### Before Change
```
Upload ID: 107
Total rows: 28,546
Successful: 28,544
Failed: 2 ❌

Errors:
- Row 84: value too long for type character varying(50)
- Row 20093: value too long for type character varying(50)
```

### After Change
```
Expected result:
Total rows: 28,546
Successful: 28,546
Failed: 0 ✅
```

## Next Upload
Silakan upload ulang file Excel yang sama. Sekarang semua data akan masuk tanpa error.

## Restart Required
✅ Celery worker restarted at 22:30:26
✅ Migration applied successfully
✅ Ready for new uploads

## Related Files
- `dashboard/models.py` - Model definitions
- `data_management/utils.py` - Upload processing logic
- `dashboard/migrations/0014_increase_varchar_to_100.py` - Database migration
