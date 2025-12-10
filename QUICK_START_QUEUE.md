# 🚀 Quick Start Guide - Task Queue Implementation

## Untuk Pembimbing / Testing

Ini adalah panduan cepat untuk menjalankan dan testing implementasi **Task Queue** dengan **Celery + Redis**.

---

## 🎯 Apa yang Sudah Diimplementasikan?

### Before (Tanpa Queue)
```
User Upload File → [WAIT 30-60 detik] → Proses selesai → Redirect
                    ⏳ User harus menunggu
```

### After (Dengan Queue)
```
User Upload File → [2-3 detik] → Redirect ke History
                   ✅ Instant feedback!
                   
[Background] 
Worker proses data → Update status → Auto-refresh halaman
```

---

## 📦 Quick Start (3 Terminal)

### Terminal 1: Redis Server
```powershell
# Option 1: Menggunakan WSL (Recommended)
wsl
sudo service redis-server start

# Option 2: Docker
docker run -d -p 6379:6379 --name redis redis:alpine

# Check Redis Running
redis-cli ping
# Expected output: PONG
```

### Terminal 2: Django Server
```powershell
cd "e:\BRI\Performance Highlight SME Dashboard"
python manage.py runserver
```

### Terminal 3: Celery Worker
```powershell
cd "e:\BRI\Performance Highlight SME Dashboard"
celery -A config worker --loglevel=info --pool=solo
```

---

## ✅ Testing Scenario

### 1. Upload Data (User Experience)

1. Buka browser: http://localhost:8000/data-management/upload/
2. Pilih file Excel/CSV
3. Click "Upload File"
4. **Perhatikan:**
   - ✅ Upload selesai dalam 2-3 detik (tidak menunggu processing!)
   - ✅ Notifikasi muncul: "File berhasil diupload! Data sedang diproses di background"
   - ✅ Auto redirect ke Upload History

### 2. Monitor Status (Real-time)

1. Di halaman Upload History, lihat status:
   - **⏱️ Queued** (Dalam Antrian) - File baru masuk
   - **⚙️ Processing** (Sedang Diproses) - Worker sedang kerja
   - **✅ Completed** (Selesai) - Proses sukses
   - **❌ Failed** (Gagal) - Ada error

2. Halaman auto-refresh setiap 5 detik jika ada task yang berjalan

3. Notifikasi "Auto-refresh aktif" muncul di kanan atas

### 3. Monitor di Celery Worker

Di **Terminal 3** (Celery Worker), lihat log:

```
[2025-12-08 10:30:00] Received task: data_management.process_uploaded_data[abc123]
[2025-12-08 10:30:01] Starting data processing for upload ID: 123
[2025-12-08 10:30:01] Processing row 1/1000...
[2025-12-08 10:30:05] Processing row 500/1000...
[2025-12-08 10:30:10] Processing row 1000/1000...
[2025-12-08 10:30:15] Data processing completed for upload ID: 123
[2025-12-08 10:30:15] Task succeeded in 15.2s
```

### 4. Check Dashboard Loading

1. Buka halaman dashboard: http://localhost:8000/dashboard/os/
2. **Perhatikan:**
   - ✅ Loading overlay muncul saat halaman mulai load
   - ✅ Spinner animation dengan text "Memuat data visualisasi..."
   - ✅ Loading hilang setelah halaman selesai load
   - ✅ User experience lebih smooth

---

## 📊 Demo Flow

```
┌─────────────────────────────────────────────────────────────┐
│  USER                    DJANGO              CELERY WORKER   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. Upload File                                               │
│       │                                                       │
│       ├──────────>  Save file to media/                      │
│       │             Create UploadHistory (status='queued')   │
│       │             Send task to Redis Queue                 │
│       │             Return response (3 sec)                  │
│       │                                                       │
│  2. <── Success! ──┘                                         │
│     Redirect to History                                      │
│                                                               │
│  3. View History                                              │
│     Status: ⏱️ Queued                                        │
│                                       │                       │
│                                       ├──> Get task from Redis
│                                       │    Update status:     │
│                                       │    'processing'       │
│                                       │    Process data...    │
│                                       │    (30-60 sec)       │
│                                       │    Update status:     │
│                                       │    'completed'        │
│                                       │                       │
│  4. [Auto-refresh]                    │                       │
│     Status: ✅ Completed               │                       │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 Troubleshooting

### Redis Not Running?
```bash
# Check
redis-cli ping

# Start (WSL)
wsl
sudo service redis-server start

# Start (Docker)
docker start redis
```

### Celery Worker Not Processing?
```bash
# Check active tasks
celery -A config inspect active

# Restart worker
# Ctrl+C di Terminal 3
celery -A config worker --loglevel=info --pool=solo
```

### Upload Still Slow?
- Pastikan Celery worker running
- Check log di Terminal 3
- Verify Redis connection: `redis-cli ping`

---

## 📈 Performance Comparison

### Before Queue Implementation
| Metric | Value |
|--------|-------|
| Upload response time | 30-60 seconds |
| User must wait | Yes ⏳ |
| Server load during upload | High (blocking) |
| Scalability | Limited |

### After Queue Implementation
| Metric | Value |
|--------|-------|
| Upload response time | 2-3 seconds ✅ |
| User must wait | No 🚀 |
| Server load during upload | Low (async) |
| Scalability | High (add more workers) |

---

## 🎨 User Experience Improvements

### 1. Instant Feedback
- User tidak perlu menunggu processing selesai
- Upload response dalam 2-3 detik
- Bisa langsung lakukan aktivitas lain

### 2. Real-time Status Updates
- Status badge dengan icon dan warna
- Auto-refresh otomatis saat ada task berjalan
- Notifikasi "Auto-refresh aktif"

### 3. Dashboard Loading Indicator
- Loading overlay dengan spinner
- Message "Memuat data visualisasi..."
- Smooth transition saat selesai

### 4. Better Error Handling
- Task yang gagal tidak crash Django server
- Error log tersimpan di UploadHistory
- Bisa retry dengan upload ulang

---

## 📝 Code Changes Summary

### New Files
- `config/celery.py` - Celery configuration
- `data_management/tasks.py` - Background tasks
- `CELERY_SETUP.md` - Full documentation

### Modified Files
- `config/__init__.py` - Import celery app
- `config/settings.py` - Add CELERY_* settings
- `requirements.txt` - Add celery, redis, django-celery-results
- `data_management/views.py` - Use async task
- `data_management/models.py` - Add 'queued' status
- `templates/base.html` - Add global loading overlay
- `templates/data_management/upload_history.html` - Add auto-refresh

---

## 🚀 Next Steps (Optional Enhancements)

1. **Celery Beat** - Scheduled tasks (cleanup old uploads)
2. **Flower** - Web-based monitoring dashboard
3. **Task Priority** - High priority untuk file kecil
4. **Progress Bar** - Real-time upload progress
5. **Email Notification** - Notify user saat processing selesai

---

## ✅ Checklist untuk Pembimbing

- [ ] Redis server berjalan
- [ ] Django server berjalan
- [ ] Celery worker berjalan
- [ ] Upload file test
- [ ] Status berubah dari queued → processing → completed
- [ ] Auto-refresh bekerja
- [ ] Dashboard loading muncul
- [ ] Check log di Celery worker

---

## 📞 Demo Notes

**Key Points to Show:**
1. Upload instant (tidak nunggu lama)
2. Status real-time di Upload History
3. Auto-refresh otomatis
4. Dashboard loading smooth
5. Celery worker log (background process)

**Feedback dari Pembimbing:**
✅ User experience lebih nyaman  
✅ Upload tidak blocking  
✅ Pemisahan task jelas (upload vs processing)  
✅ Loading indicator informatif  

---

Semoga implementasi ini sesuai dengan feedback pembimbing! 🎉
