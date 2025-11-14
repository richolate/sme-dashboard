# Quick Start Guide - Dashboard Performance Highlights SME

## 🚀 Langkah Cepat untuk Mulai

### 1. Setup Virtual Environment & Install Dependencies

```powershell
# Masuk ke direktori project
cd "E:\BRI\Performance Highlight SME Dashboard"

# Buat virtual environment
python -m venv venv

# Aktifkan virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup PostgreSQL

#### Opsi A: Quick Setup (Gunakan user postgres default)

```powershell
# Login ke psql
psql -U postgres

# Di dalam psql, jalankan:
CREATE DATABASE sme_dashboard;
\q
```

#### Opsi B: Setup dengan User Baru (Recommended untuk Production)

```powershell
# Login ke psql
psql -U postgres

# Di dalam psql, jalankan:
CREATE DATABASE sme_dashboard;
CREATE USER sme_admin WITH PASSWORD 'password123';
GRANT ALL PRIVILEGES ON DATABASE sme_dashboard TO sme_admin;
\q
```

### 3. Konfigurasi Environment

```powershell
# Copy .env.example ke .env
copy .env.example .env

# Edit .env dengan notepad atau text editor lain
notepad .env
```

Isi `.env` dengan:
```env
SECRET_KEY=django-insecure-change-this-to-random-string
DEBUG=True

DB_NAME=sme_dashboard
DB_USER=postgres
DB_PASSWORD=your_postgres_password_here
DB_HOST=localhost
DB_PORT=5432
```

### 4. Migrasi Database

```powershell
python manage.py makemigrations
python manage.py migrate
```

### 5. Buat Admin User

```powershell
python manage.py createsuperuser
```

Input:
- Username: `admin`
- Email: `admin@bri.co.id`
- Password: (masukkan password anda)

### 6. Set User sebagai Admin

```powershell
python manage.py shell
```

```python
from accounts.models import User
user = User.objects.get(username='admin')
user.role = 'admin'
user.save()
exit()
```

### 7. Jalankan Server

```powershell
python manage.py runserver
```

### 8. Akses Website

Buka browser: **http://127.0.0.1:8000**

Login dengan:
- Username: `admin`
- Password: (password yang dibuat di step 5)

---

## ✅ Checklist

- [ ] Virtual environment dibuat dan diaktifkan
- [ ] Dependencies terinstall
- [ ] PostgreSQL database dibuat
- [ ] File .env dikonfigurasi
- [ ] Migrasi database berhasil
- [ ] Superuser dibuat
- [ ] User role diset sebagai admin
- [ ] Server berjalan
- [ ] Bisa login ke website

---

## 🎯 Test Koneksi PostgreSQL

Buat file `test_connection.py`:

```python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print("✅ PostgreSQL Connected!")
        print(f"Version: {version[0]}")
except Exception as e:
    print(f"❌ Connection Failed: {e}")
```

Jalankan:
```powershell
python test_connection.py
```

---

## 📝 Contoh Membuat User Biasa (Role: User)

```powershell
python manage.py shell
```

```python
from accounts.models import User

# Buat user dengan role 'user'
User.objects.create_user(
    username='user1',
    email='user1@bri.co.id',
    password='password123',
    first_name='User',
    last_name='Satu',
    role='user'
)

exit()
```

---

## 🔄 Commands Cheat Sheet

```powershell
# Aktifkan virtual environment
.\venv\Scripts\activate

# Jalankan server
python manage.py runserver

# Buat migrasi
python manage.py makemigrations

# Jalankan migrasi
python manage.py migrate

# Buat superuser
python manage.py createsuperuser

# Shell Django
python manage.py shell

# Collect static files
python manage.py collectstatic

# Check database
python manage.py dbshell
```

---

## 🐛 Common Issues & Solutions

### Issue: psycopg2 error

**Solution:**
```powershell
pip install psycopg2-binary --force-reinstall
```

### Issue: Port 8000 already in use

**Solution:**
```powershell
# Gunakan port lain
python manage.py runserver 8001
```

### Issue: Can't activate virtual environment

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: Database connection refused

**Solution:**
- Pastikan PostgreSQL service running
- Check username/password di .env
- Check port 5432 available

---

## 📱 Akses Menu

Setelah login sebagai **Admin**, Anda akan melihat menu:

**Dashboard:**
- Dashboard Utama
- Dashboard OS
- Dashboard Summary (dengan 3 sub-tab)
- Grafik Harian

**Data Management:**
- Upload Data
- Riwayat Upload
- Hapus Data

Login sebagai **User** hanya akan melihat menu Dashboard.

---

**Selamat menggunakan Dashboard Performance Highlights SME!** 🎉
