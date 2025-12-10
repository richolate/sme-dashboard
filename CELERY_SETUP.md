# Setup dan Cara Menjalankan Task Queue (Celery + Redis)

## 📋 Daftar Isi
1. [Prerequisites](#prerequisites)
2. [Install Redis di Windows](#install-redis-di-windows)
3. [Menjalankan Aplikasi](#menjalankan-aplikasi)
4. [Monitoring Tasks](#monitoring-tasks)
5. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Dependencies yang Sudah Terinstall
```bash
celery==5.4.0
redis==5.2.0
django-celery-results==2.5.1
```

---

## Install Redis di Windows

### Option 1: Menggunakan Windows Subsystem for Linux (WSL) - **RECOMMENDED**

1. **Install WSL**
   ```powershell
   wsl --install
   ```

2. **Install Redis di WSL**
   ```bash
   sudo apt update
   sudo apt install redis-server
   ```

3. **Start Redis**
   ```bash
   sudo service redis-server start
   ```

4. **Cek Redis Berjalan**
   ```bash
   redis-cli ping
   # Output: PONG
   ```

### Option 2: Menggunakan Memurai (Redis fork untuk Windows Native)

1. Download Memurai dari: https://www.memurai.com/get-memurai
2. Install dan jalankan sebagai Windows Service
3. Default port: `6379`

### Option 3: Docker (Jika sudah punya Docker Desktop)

```bash
docker run -d -p 6379:6379 --name redis redis:alpine
```

---

## Menjalankan Aplikasi

### Step 1: Jalankan Redis Server

**Jika menggunakan WSL:**
```bash
wsl
sudo service redis-server start
```

**Jika menggunakan Memurai:**
- Redis akan otomatis berjalan sebagai Windows Service

**Jika menggunakan Docker:**
```bash
docker start redis
```

### Step 2: Jalankan Django Server

```powershell
# Terminal 1 - Django Server
cd "e:\BRI\Performance Highlight SME Dashboard"
python manage.py runserver
```

### Step 3: Jalankan Celery Worker

```powershell
# Terminal 2 - Celery Worker
cd "e:\BRI\Performance Highlight SME Dashboard"
celery -A config worker --loglevel=info --pool=solo
```

> **Note untuk Windows:** Gunakan `--pool=solo` karena Windows tidak support prefork pool

### Step 4 (Opsional): Jalankan Celery Beat (untuk scheduled tasks)

```powershell
# Terminal 3 - Celery Beat (optional)
cd "e:\BRI\Performance Highlight SME Dashboard"
celery -A config beat --loglevel=info
```

---

## Cara Kerja System

### Flow Upload Data

```
User Upload File
     ↓
File disimpan ke media/uploads/
     ↓
UploadHistory dibuat (status: 'queued')
     ↓
Task dikirim ke Celery Queue
     ↓
User mendapat notifikasi: "File berhasil diupload, sedang diproses..."
     ↓
User redirect ke Upload History
     ↓
[BACKGROUND PROCESS]
Celery Worker mengambil task
     ↓
Status berubah: 'queued' → 'processing'
     ↓
Proses file dengan pandas (parse, validate, insert ke DB)
     ↓
Status berubah: 'processing' → 'completed' / 'failed'
     ↓
Upload History page auto-refresh setiap 5 detik
```

### Status Workflow

- **queued**: File sudah diupload, menunggu diproses
- **processing**: Sedang diproses oleh Celery worker
- **completed**: Proses selesai sukses
- **failed**: Proses gagal (lihat error log)

---

## Monitoring Tasks

### 1. Check Redis Connection
```bash
redis-cli ping
# Expected: PONG
```

### 2. Monitor Celery Worker
Lihat di terminal tempat Celery worker berjalan, akan muncul log seperti:
```
[2025-12-08 10:30:00,000: INFO/MainProcess] Task data_management.process_uploaded_data[abc123] received
[2025-12-08 10:30:05,000: INFO/MainProcess] Task data_management.process_uploaded_data[abc123] succeeded
```

### 3. Check Task Results di Django Admin
- Buka: http://localhost:8000/admin/
- Navigasi ke: DJANGO CELERY RESULTS → Task results
- Lihat semua task yang pernah dijalankan

### 4. Auto-Refresh Upload History
- Buka halaman Upload History
- Jika ada task yang masih processing/queued, halaman akan auto-refresh setiap 5 detik
- Notifikasi "Auto-refresh aktif" akan muncul

---

## Monitoring di Production

### Menggunakan Flower (Celery Monitoring Tool)

1. **Install Flower**
   ```bash
   pip install flower
   ```

2. **Jalankan Flower**
   ```powershell
   celery -A config flower
   ```

3. **Akses Dashboard**
   - Buka: http://localhost:5555
   - Lihat real-time task monitoring, worker status, dll

---

## Troubleshooting

### Problem 1: Redis Connection Error
```
Error: ConnectionRefusedError: [WinError 10061]
```

**Solution:**
- Pastikan Redis server sudah berjalan
- Check dengan: `redis-cli ping`
- Jika pakai WSL: `wsl` → `sudo service redis-server start`

### Problem 2: Celery Worker Tidak Menerima Task
```
Task sent but not being processed
```

**Solution:**
- Restart Celery worker
- Pastikan nama app benar: `celery -A config worker`
- Check log di terminal Celery worker

### Problem 3: Import Error ModuleNotFoundError
```
ModuleNotFoundError: No module named 'celery'
```

**Solution:**
```bash
pip install celery redis django-celery-results
```

### Problem 4: Pool Not Supported on Windows
```
ValueError: Pool implementation not available
```

**Solution:**
Gunakan `--pool=solo`:
```bash
celery -A config worker --loglevel=info --pool=solo
```

### Problem 5: Task Stuck di "queued"
**Solution:**
- Check Celery worker masih running
- Restart Celery worker
- Check Redis: `redis-cli keys *`

---

## Testing Upload

### Test Manual
1. Buka http://localhost:8000/data-management/upload/
2. Upload file Excel/CSV
3. Perhatikan notifikasi: "File berhasil diupload, sedang diproses..."
4. Redirect ke Upload History
5. Status awal: **Queued** (⏱️ Dalam Antrian)
6. Tunggu beberapa detik...
7. Status berubah: **Processing** (⚙️ Sedang Diproses)
8. Setelah selesai: **Completed** (✅ Selesai)
9. Halaman auto-refresh hingga status selesai

### Check di Celery Worker Log
```
[2025-12-08 10:30:00] INFO/MainProcess] Received task: data_management.process_uploaded_data
[2025-12-08 10:30:01] INFO/ForkPoolWorker-1] Starting data processing for upload ID: 123
[2025-12-08 10:30:15] INFO/ForkPoolWorker-1] Data processing completed for upload ID: 123
[2025-12-08 10:30:15] INFO/MainProcess] Task succeeded
```

---

## Environment Variables

Add to `.env` file (optional, sudah ada default):
```ini
# Redis Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

---

## Production Deployment

### Systemd Service (Linux Production)

**redis.service**
```ini
[Unit]
Description=Redis In-Memory Data Store
After=network.target

[Service]
Type=notify
ExecStart=/usr/bin/redis-server /etc/redis/redis.conf
Restart=always

[Install]
WantedBy=multi-user.target
```

**celery.service**
```ini
[Unit]
Description=Celery Service
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/path/to/project
ExecStart=/path/to/venv/bin/celery -A config worker --loglevel=info --detach

[Install]
WantedBy=multi-user.target
```

---

## Summary Commands

### Development (Windows)

```powershell
# Terminal 1: Redis (WSL)
wsl
sudo service redis-server start

# Terminal 2: Django
cd "e:\BRI\Performance Highlight SME Dashboard"
python manage.py runserver

# Terminal 3: Celery Worker
cd "e:\BRI\Performance Highlight SME Dashboard"
celery -A config worker --loglevel=info --pool=solo
```

### Quick Check
```bash
# Check Redis
redis-cli ping

# Check Celery
celery -A config inspect active

# Check Django
python manage.py check
```

---

## Keuntungan Menggunakan Task Queue

✅ **Upload lebih cepat** - User tidak perlu menunggu proses selesai  
✅ **Better UX** - User bisa langsung melakukan aktivitas lain  
✅ **Scalable** - Bisa menambah worker untuk proses paralel  
✅ **Monitoring** - Status realtime di Upload History  
✅ **Error handling** - Jika gagal, bisa retry otomatis  
✅ **Background processing** - Tidak block Django request/response cycle  

---

## Contact & Support

Jika ada masalah atau pertanyaan:
- Check log Celery worker
- Check log Django server
- Check Redis connection
- Lihat error_log di Upload History

Happy coding! 🚀
