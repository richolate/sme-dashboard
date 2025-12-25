# SME Dashboard - Performance Highlight# 📊 Dashboard Performance Highlights SME



Django-based dashboard untuk monitoring performance SME (Small Medium Enterprise) dengan visualisasi data real-time.![Django](https://img.shields.io/badge/Django-4.2.7-green.svg)

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-blue.svg)

## 🚀 Quick Start![Python](https://img.shields.io/badge/Python-3.10+-yellow.svg)

![License](https://img.shields.io/badge/License-BRI%20Internal-red.svg)

### Prerequisites

- Python 3.8+Dashboard untuk monitoring dan analisis data pinjaman SME menggunakan Django dan PostgreSQL.

- PostgreSQL 12+

- Redis Server## 📋 Deskripsi



### InstallationSistem dashboard interaktif untuk mengelola dan menganalisis data pinjaman nasabah SME dengan fitur:

- **Role-based Access Control** (Admin & User)

1. Clone dan setup environment:- **Multiple Dashboard Views** (OS, Summary, Grafik Harian)

```bash- **Data Management** (Upload, History, Delete)

python -m venv venv- **PostgreSQL Integration** untuk handling data skala besar (10+ juta baris)

venv\Scripts\activate- **Responsive UI** dengan Bootstrap 5

pip install -r requirements.txt

```## 🚀 Fitur Utama



2. Configure database (.env):### Dashboard

```env1. **Dashboard OS** - Monitoring Outstanding pinjaman

DATABASE_URL=postgresql://postgres:password@localhost:5432/sme_dashboard2. **Dashboard Summary** - Ringkasan data dengan 3 sub-kategori:

CELERY_BROKER_URL=redis://localhost:6379/0   - Summary Medium Only

```   - Summary Konsol

   - Summary Only

3. Run migrations:3. **Dashboard Grafik Harian** - Trend dan analisis harian

```bash

python manage.py migrate### Role & Permissions

python manage.py createsuperuser

```#### Admin

- ✅ Akses semua dashboard

4. Start services:- ✅ Upload data pinjaman (Excel/CSV)

```bash- ✅ Lihat riwayat upload

# Terminal 1 - Django- ✅ Hapus data

python manage.py runserver

#### User

# Terminal 2 - Celery- ✅ Akses semua dashboard (read-only)

celery -A config worker --loglevel=info --pool=solo

```## 📦 Prerequisites



## 📊 Features- Python 3.10 atau lebih tinggi

- PostgreSQL 12 atau lebih tinggi

- Real-time metrics: OS, DPK, NPL, LAR, LR, NSB- pip (Python package manager)

- Data segmentation: SMALL, MEDIUM, COMMERCIAL- Virtual environment (recommended)

- Excel/CSV upload with background processing

- Dynamic date filtering## 🔧 Instalasi

- User authentication

### 1. Clone atau Download Project

## 🗂️ Structure

```powershell

```cd "E:\BRI\Performance Highlight SME Dashboard"

├── dashboard/          # Main app dengan formulas & views```

├── data_management/    # Upload & Celery tasks

├── accounts/           # Authentication### 2. Setup Virtual Environment

└── config/             # Settings & Celery config

``````powershell

# Buat virtual environment

## 📈 Key Metricspython -m venv venv



| Metric | Description |# Aktifkan virtual environment

|--------|-------------|.\venv\Scripts\activate

| OS     | Outstanding loan balance |```

| DPK    | Special mention (kol_adk=2) |

| NPL    | Non-performing (kol_adk=3,4,5) |### 3. Install Dependencies

| LAR    | Loan at Risk (DPK+NPL+LR) |

| NSB    | Nasabah count (SUM where DUB_NASABAH='TRUE') |```powershell

pip install -r requirements.txt

## 📤 Data Upload```



Required Excel columns:### 4. Setup PostgreSQL Database

- PERIODE (DD/MM/YYYY)

- KANCA, KODE UKER, UKER#### A. Install PostgreSQL (jika belum)

- NOMOR REKENING, NAMA DEBITUR1. Download PostgreSQL dari: https://www.postgresql.org/download/windows/

- KOLEKTIBILITAS (LANCAR, DPK, KURANG LANCAR, DIRAGUKAN, MACET)2. Install PostgreSQL dengan default settings

- OS, NASABAH, DUB NASABAH3. Catat password untuk user `postgres`

- And more...

#### B. Buat Database

## 🛠️ Maintenance

Buka **pgAdmin** atau **psql** command line:

Clear cache:

```bash**Menggunakan psql:**

python manage.py shell```powershell

>>> from django.core.cache import cache# Login ke PostgreSQL

>>> cache.clear()psql -U postgres

```

# Buat database

Database backup:CREATE DATABASE sme_dashboard;

```bash

pg_dump sme_dashboard > backup.sql# Buat user (optional, atau gunakan postgres user)

```CREATE USER sme_admin WITH PASSWORD 'your_password';



## License# Berikan privileges

GRANT ALL PRIVILEGES ON DATABASE sme_dashboard TO sme_admin;

Bank BRI Internal Use Only

# Keluar
\q
```

**Menggunakan pgAdmin:**
1. Buka pgAdmin
2. Klik kanan pada "Databases" → Create → Database
3. Nama database: `sme_dashboard`
4. Owner: `postgres` atau user lain
5. Save

### 5. Konfigurasi Environment Variables

```powershell
# Copy file .env.example menjadi .env
copy .env.example .env
```

Edit file `.env` dengan text editor dan sesuaikan konfigurasi:

```env
SECRET_KEY=django-insecure-ganti-dengan-secret-key-anda
DEBUG=True

# PostgreSQL Database Configuration
DB_NAME=sme_dashboard
DB_USER=postgres
DB_PASSWORD=password_postgresql_anda
DB_HOST=localhost
DB_PORT=5432
```

**Generate SECRET_KEY:**
```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 6. Migrasi Database

```powershell
# Buat file migrasi
python manage.py makemigrations

# Jalankan migrasi
python manage.py migrate
```

### 7. Buat Superuser (Admin)

```powershell
python manage.py createsuperuser
```

Ikuti prompt:
- Username: admin
- Email: admin@example.com
- Password: (password anda)
- Role akan otomatis di-set sebagai 'user', ubah nanti via Django Admin

### 8. Collect Static Files (Optional untuk development)

```powershell
python manage.py collectstatic
```

## ▶️ Menjalankan Server

```powershell
# Pastikan virtual environment aktif
.\venv\Scripts\activate

# Jalankan development server
python manage.py runserver
```

Buka browser dan akses: **http://127.0.0.1:8000**

## 👤 Setup User Roles

### Cara 1: Via Django Admin

1. Akses Django Admin: http://127.0.0.1:8000/admin
2. Login dengan superuser
3. Klik **Users**
4. Pilih user yang ingin diubah
5. Scroll ke bagian **Additional Info**
6. Ubah field **Role** menjadi `admin` atau `user`
7. Save

### Cara 2: Via Django Shell

```powershell
python manage.py shell
```

```python
from accounts.models import User

# Ubah role user menjadi admin
user = User.objects.get(username='admin')
user.role = 'admin'
user.save()

# Buat user baru dengan role user
user = User.objects.create_user(
    username='user1',
    email='user1@example.com',
    password='password123',
    role='user'
)

# Keluar
exit()
```

## 🔌 Koneksi PostgreSQL - Detail

### Testing Koneksi

Buat file `test_db_connection.py` di root project:

```python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

try:
    cursor = connection.cursor()
    cursor.execute("SELECT version();")
    db_version = cursor.fetchone()
    print(f"✅ Koneksi PostgreSQL berhasil!")
    print(f"PostgreSQL version: {db_version[0]}")
except Exception as e:
    print(f"❌ Koneksi gagal: {e}")
```

Jalankan:
```powershell
python test_db_connection.py
```

### Troubleshooting PostgreSQL

#### Error: "FATAL: password authentication failed"
- Pastikan password di `.env` benar
- Check `pg_hba.conf` untuk authentication method
- Restart PostgreSQL service

#### Error: "could not connect to server"
- Pastikan PostgreSQL service berjalan
- Check port 5432 tidak digunakan aplikasi lain
- Firewall mungkin blocking koneksi

#### Error: "database does not exist"
- Buat database terlebih dahulu: `CREATE DATABASE sme_dashboard;`

### Monitoring Database

```powershell
# Via psql
psql -U postgres -d sme_dashboard

# Lihat semua tabel
\dt

# Lihat detail tabel
\d nama_tabel

# Hitung jumlah data
SELECT COUNT(*) FROM LW321;
```

## 📊 Upload Data

### Format File

File upload harus memiliki kolom-kolom berikut (sesuaikan dengan struktur 38 kolom Anda):

| Kolom | Tipe Data | Wajib | Deskripsi |
|-------|-----------|-------|-----------|
| periode | String | Ya | Periode laporan (mis. `2024-01`) |
| kanca | String | Tidak | Nama kantor cabang |
| kode_uker | String | Tidak | Kode unit kerja |
| uker | String | Tidak | Nama unit kerja |
| ln_type | String | Tidak | Jenis lini produk/pinjaman |
| nomor_rekening | String | Ya | Nomor rekening unik debitur |
| nama_debitur | String | Tidak | Nama debitur |
| plafon | Decimal | Tidak | Nilai plafon kredit |
| next_pmt_date | Date | Tidak | Tanggal jatuh tempo pembayaran pokok berikutnya |
| next_int_pmt_date | Date | Tidak | Tanggal jatuh tempo pembayaran bunga berikutnya |
| rate | Decimal | Tidak | Suku bunga (dalam persen) |
| tgl_menunggak | Date | Tidak | Tanggal mulai tunggakan (jika ada) |
| tgl_realisasi | Date | Tidak | Tanggal realisasi kredit |
| tgl_jatuh_tempo | Date | Tidak | Tanggal jatuh tempo kredit |
| jangka_waktu | Integer | Tidak | Lama kredit (bulan) |
| flag_restruk | String | Tidak | Penanda restrukturisasi (Ya/Tidak) |
| cif_no | String | Ya | CIF nasabah |
| kolektibilitas_lancar | String | Tidak | Flag kolektibilitas Lancar (1/0) |
| kolektibilitas_dpk | String | Tidak | Flag kolektibilitas Dalam Perhatian Khusus |
| kolektibilitas_kurang_lancar | String | Tidak | Flag kolektibilitas Kurang Lancar |
| kolektibilitas_diragukan | String | Tidak | Flag kolektibilitas Diragukan |
| kolektibilitas_macet | String | Tidak | Flag kolektibilitas Macet |
| tunggakan_pokok | Decimal | Tidak | Nilai tunggakan pokok |
| tunggakan_bunga | Decimal | Tidak | Nilai tunggakan bunga |
| tunggakan_pinalti | Decimal | Tidak | Nilai tunggakan denda/pinalti |
| code | String | Tidak | Kode klasifikasi internal |
| description | String | Tidak | Deskripsi tambahan |
| kol_adk | String | Tidak | Kode KOL ADK |
| pn_pengelola_singlepn | String | Tidak | PN pengelola utama |
| pn_pengelola_1 | String | Tidak | PN pengelola 1 |
| pn_pemrakarsa | String | Tidak | PN pemrakarsa |
| pn_referral | String | Tidak | PN referral |
| pn_restruk | String | Tidak | PN restrukturisasi |
| pn_pengelola_2 | String | Tidak | PN pengelola 2 |
| pn_pemutus | String | Tidak | PN pemutus |
| pn_crm | String | Tidak | PN CRM |
| pn_rm_referral_naik_segmentasi | String | Tidak | PN RM referral naik segmentasi |
| pn_rm_crr | String | Tidak | PN RM CRR |

### Cara Upload

1. Login sebagai **Admin**
2. Klik menu **Upload Data**
3. Pilih file (.xlsx, .xls, atau .csv)
4. Tambahkan catatan (optional)
5. Klik **Upload**

## 📁 Struktur Project

```
Performance Highlight SME Dashboard/
├── config/                      # Konfigurasi Django
│   ├── __init__.py
│   ├── settings.py             # Settings utama
│   ├── urls.py                 # URL routing utama
│   ├── wsgi.py
│   └── asgi.py
├── accounts/                    # App untuk user management
│   ├── models.py               # Custom User model
│   ├── views.py                # Login/Logout views
│   ├── urls.py
│   └── admin.py
├── dashboard/                   # App untuk dashboard
│   ├── models.py               # LW321, ProcessedData models
│   ├── views.py                # Dashboard views
│   ├── urls.py
│   └── admin.py
├── data_management/            # App untuk data management
│   ├── models.py               # UploadHistory model
│   ├── views.py                # Upload, History, Delete views
│   ├── forms.py                # Upload form
│   ├── utils.py                # Data processing utilities
│   ├── urls.py
│   └── admin.py
├── drizzle/                    # Drizzle Studio helper project untuk eksplorasi DB
├── templates/                  # HTML templates
│   ├── base.html              # Base template
│   ├── accounts/
│   │   └── login.html
│   ├── dashboard/
│   │   ├── home.html
│   │   ├── dashboard_os.html
│   │   ├── dashboard_summary.html
│   │   └── dashboard_grafik_harian.html
│   └── data_management/
│       ├── upload_data.html
│       ├── upload_history.html
│       └── delete_data.html
├── static/                     # Static files (CSS, JS, images)
├── media/                      # User uploaded files
├── manage.py                   # Django management script
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
├── .env.example               # Environment variables template
├── .gitignore
└── README.md
```

## 🔐 Security Notes

### Production Deployment

Untuk production, ubah setting berikut di `.env`:

```env
DEBUG=False
SECRET_KEY=<generate-strong-secret-key>
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

Dan update `settings.py`:

```python
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')
```

### Database Security

1. Jangan gunakan user `postgres` untuk aplikasi production
2. Buat user database khusus dengan privileges terbatas
3. Gunakan SSL connection untuk PostgreSQL di production
4. Backup database secara regular

## 📝 Customization

### Menambahkan Kolom di Model LW321

Edit `dashboard/models.py`:

```python
class LW321(models.Model):
    # ... kolom existing ...
    
    # Tambahkan kolom baru sesuai kebutuhan (total 38 kolom)
    new_column = models.CharField(max_length=100)
```

Lalu jalankan migrasi:
```powershell
python manage.py makemigrations
python manage.py migrate
```

### Mengubah Proses Upload Data

Edit `data_management/utils.py` function `process_uploaded_file()` untuk menyesuaikan dengan struktur file Anda.

## 🐛 Troubleshooting

### Virtual Environment Issues

```powershell
# Jika venv tidak bisa diaktifkan, enable execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Migration Errors

```powershell
# Reset migrations (hati-hati, akan hapus data!)
python manage.py migrate --fake <app_name> zero
python manage.py migrate <app_name>
```

### Static Files Not Loading

```powershell
# Collect static files
python manage.py collectstatic --clear
```

## 📞 Support

Untuk pertanyaan atau issue, silakan hubungi tim development.

## 📄 License

Internal BRI Project - All Rights Reserved

---

**Dashboard Performance Highlights SME** © 2025 BRI
