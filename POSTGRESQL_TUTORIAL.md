# Tutorial Koneksi PostgreSQL untuk Dashboard SME

## 📚 Panduan Lengkap PostgreSQL Setup

### 1️⃣ Install PostgreSQL

#### Windows:

1. **Download PostgreSQL**
   - Kunjungi: https://www.postgresql.org/download/windows/
   - Download installer PostgreSQL versi terbaru (recommended: 14.x atau 15.x)

2. **Install PostgreSQL**
   - Jalankan installer
   - Ikuti wizard instalasi:
     - Installation Directory: Default (C:\Program Files\PostgreSQL\15)
     - Components: Pilih semua (PostgreSQL Server, pgAdmin 4, Command Line Tools)
     - Data Directory: Default
     - **Password**: Masukkan password untuk superuser `postgres` (CATAT PASSWORD INI!)
     - Port: 5432 (default)
     - Locale: Default
   - Klik Next sampai selesai

3. **Verifikasi Instalasi**
   ```powershell
   # Cek versi PostgreSQL
   psql --version
   ```

### 2️⃣ Konfigurasi PostgreSQL

#### Menggunakan pgAdmin 4 (GUI)

1. **Buka pgAdmin 4**
   - Cari di Start Menu: "pgAdmin 4"
   - Masukkan master password (buat baru jika pertama kali)

2. **Connect ke PostgreSQL Server**
   - Expand "Servers" di sidebar kiri
   - Klik "PostgreSQL 15" (atau versi yang terinstall)
   - Masukkan password postgres

3. **Buat Database**
   - Klik kanan pada "Databases"
   - Pilih "Create" → "Database..."
   - Isi form:
     - Database: `sme_dashboard`
     - Owner: `postgres`
     - Encoding: `UTF8`
   - Save

4. **Buat User Khusus (Optional tapi Recommended)**
   - Klik kanan pada "Login/Group Roles"
   - Pilih "Create" → "Login/Group Role..."
   - Tab "General":
     - Name: `sme_admin`
   - Tab "Definition":
     - Password: `yourpassword123`
   - Tab "Privileges":
     - Can login?: Yes
     - Superuser?: No
     - Create databases?: Yes
   - Save

5. **Berikan Akses ke Database**
   - Expand "Databases" → "sme_dashboard"
   - Klik kanan pada database → "Properties"
   - Tab "Security":
     - Grantee: `sme_admin`
     - Privileges: ALL
   - Save

#### Menggunakan Command Line (psql)

```powershell
# Login ke PostgreSQL
psql -U postgres

# Buat database
CREATE DATABASE sme_dashboard 
    WITH ENCODING 'UTF8'
    LC_COLLATE='English_United States.1252'
    LC_CTYPE='English_United States.1252';

# Buat user
CREATE USER sme_admin WITH PASSWORD 'yourpassword123';

# Berikan privileges
GRANT ALL PRIVILEGES ON DATABASE sme_dashboard TO sme_admin;

# Berikan akses ke schema public
\c sme_dashboard
GRANT ALL ON SCHEMA public TO sme_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO sme_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO sme_admin;

# Keluar
\q
```

### 3️⃣ Konfigurasi Django

#### Edit file `.env`

```env
SECRET_KEY=your-secret-key-here-change-this
DEBUG=True

# PostgreSQL Configuration
DB_NAME=sme_dashboard
DB_USER=sme_admin
DB_PASSWORD=yourpassword123
DB_HOST=localhost
DB_PORT=5432
```

#### Verifikasi Connection Settings

File `config/settings.py` sudah dikonfigurasi:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='sme_dashboard'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}
```

### 4️⃣ Install psycopg2

```powershell
# Aktifkan virtual environment
.\venv\Scripts\activate

# Install psycopg2 binary
pip install psycopg2-binary
```

### 5️⃣ Test Koneksi

```powershell
# Test koneksi database
python test_db_connection.py
```

Output yang diharapkan:
```
============================================================
Testing PostgreSQL Connection
============================================================

Database Configuration:
  Engine   : django.db.backends.postgresql
  Name     : sme_dashboard
  User     : sme_admin
  Host     : localhost
  Port     : 5432
  Password : ***************

✅ Connection Successful!

Database Info:
  Database : sme_dashboard
  User     : sme_admin
  Version  : PostgreSQL 15.x...
============================================================
```

### 6️⃣ Jalankan Migrasi

```powershell
# Buat file migrasi
python manage.py makemigrations

# Jalankan migrasi
python manage.py migrate
```

Output yang diharapkan:
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions, accounts, dashboard, data_management
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying accounts.0001_initial... OK
  Applying dashboard.0001_initial... OK
  Applying data_management.0001_initial... OK
  ...
```

### 7️⃣ Verifikasi Tabel di Database

#### Via pgAdmin:
1. Expand "Databases" → "sme_dashboard" → "Schemas" → "public" → "Tables"
2. Anda akan melihat tabel-tabel:
   - `users`
   - `loan_data`
   - `processed_data`
   - `upload_history`
   - dll.

#### Via psql:
```powershell
psql -U sme_admin -d sme_dashboard

# Lihat semua tabel
\dt

# Lihat struktur tabel
\d users
\d loan_data

# Keluar
\q
```

## 🔧 Troubleshooting

### Problem 1: "psql" tidak dikenali

**Solution:**
```powershell
# Tambahkan PostgreSQL ke PATH
# Lokasi default: C:\Program Files\PostgreSQL\15\bin

# Atau gunakan full path:
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres
```

### Problem 2: Password authentication failed

**Solution:**
1. Pastikan password di `.env` benar
2. Reset password user:
   ```sql
   ALTER USER sme_admin WITH PASSWORD 'newpassword';
   ```
3. Check `pg_hba.conf`:
   - Lokasi: `C:\Program Files\PostgreSQL\15\data\pg_hba.conf`
   - Pastikan ada line: `host all all 127.0.0.1/32 md5`

### Problem 3: Could not connect to server

**Solution:**
1. Check PostgreSQL service running:
   - Buka Services (Win+R → `services.msc`)
   - Cari "postgresql-x64-15"
   - Pastikan status "Running"
   - Jika tidak, klik "Start"

2. Check port:
   ```powershell
   netstat -an | findstr "5432"
   ```

### Problem 4: Database does not exist

**Solution:**
```powershell
psql -U postgres
CREATE DATABASE sme_dashboard;
\q
```

### Problem 5: Permission denied for schema public

**Solution:**
```sql
\c sme_dashboard
GRANT ALL ON SCHEMA public TO sme_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO sme_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO sme_admin;
```

## 📊 Monitoring Database

### Lihat Koneksi Aktif

```sql
SELECT * FROM pg_stat_activity WHERE datname = 'sme_dashboard';
```

### Lihat Ukuran Database

```sql
SELECT pg_size_pretty(pg_database_size('sme_dashboard'));
```

### Lihat Jumlah Records per Tabel

```sql
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    n_live_tup AS row_count
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Backup Database

```powershell
# Backup database
pg_dump -U sme_admin -d sme_dashboard -f backup.sql

# Backup dengan compression
pg_dump -U sme_admin -d sme_dashboard | gzip > backup.sql.gz

# Restore
psql -U sme_admin -d sme_dashboard -f backup.sql
```

## 🚀 Performance Optimization

### Index untuk Query Cepat

Django sudah membuat index otomatis, tapi Anda bisa tambahkan:

```sql
-- Index untuk analisis periode per kanca
CREATE INDEX idx_periode_kanca ON loan_data(periode, kanca);

-- Index untuk monitoring kolektibilitas macet per periode
CREATE INDEX idx_periode_kolektibilitas_macet ON loan_data(periode, kolektibilitas_macet);

-- Index unik nomor rekening (sudah di model, ulangi jika perlu)
CREATE UNIQUE INDEX idx_nomor_rekening ON loan_data(nomor_rekening);

-- Index tambahan untuk pencarian CIF
CREATE INDEX idx_cif_no ON loan_data(cif_no);
```

### Vacuum Database (Maintenance)

```sql
-- Analyze tables
ANALYZE;

-- Vacuum database
VACUUM ANALYZE;
```

## 🔐 Security Best Practices

### 1. Jangan gunakan user `postgres` untuk aplikasi

Buat user khusus dengan privileges minimal:

```sql
CREATE USER app_readonly WITH PASSWORD 'password';
GRANT CONNECT ON DATABASE sme_dashboard TO app_readonly;
GRANT USAGE ON SCHEMA public TO app_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_readonly;
```

### 2. Gunakan SSL Connection (Production)

Edit `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}
```

### 3. Backup Regular

Setup scheduled backup (Windows Task Scheduler):

```powershell
# backup-script.ps1
$date = Get-Date -Format "yyyyMMdd_HHmmss"
$filename = "backup_sme_dashboard_$date.sql"
& "C:\Program Files\PostgreSQL\15\bin\pg_dump.exe" -U sme_admin -d sme_dashboard -f "E:\Backups\$filename"
```

## 📈 Monitoring Tools

### pgAdmin Query Tool

1. Buka pgAdmin
2. Klik database → Tools → Query Tool
3. Jalankan query monitoring

### Database Statistics

```sql
-- Tabel terbesar
SELECT 
    table_name,
    pg_size_pretty(pg_total_relation_size(quote_ident(table_name))) AS size
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY pg_total_relation_size(quote_ident(table_name)) DESC;

-- Slow queries
SELECT 
    query,
    calls,
    total_time,
    mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

---

**Selamat! PostgreSQL sudah siap digunakan untuk Dashboard SME** 🎉
