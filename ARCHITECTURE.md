# 📐 Arsitektur & Flow Diagram

## 🏗️ Arsitektur Aplikasi

```
┌─────────────────────────────────────────────────────────────────┐
│                         BROWSER (Client)                        │
│                     http://127.0.0.1:8000                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DJANGO APPLICATION                         │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                    URL Router (urls.py)                   │ │
│  └─────────┬──────────────┬──────────────┬────────────────────┘ │
│            │              │              │                      │
│            ▼              ▼              ▼                      │
│  ┌─────────────┐ ┌──────────────┐ ┌────────────────┐          │
│  │  accounts/  │ │  dashboard/  │ │ data_management│          │
│  │  (App)      │ │  (App)       │ │     (App)      │          │
│  ├─────────────┤ ├──────────────┤ ├────────────────┤          │
│  │ • Login     │ │ • Home       │ │ • Upload Data  │          │
│  │ • Logout    │ │ • OS         │ │ • History      │          │
│  │ • User Mgmt │ │ • Summary    │ │ • Delete       │          │
│  │             │ │ • Grafik     │ │                │          │
│  └─────────────┘ └──────────────┘ └────────────────┘          │
│            │              │              │                      │
│            └──────────────┼──────────────┘                      │
│                           ▼                                     │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                    MODELS (ORM)                           │ │
│  │  • User          • LoanData      • UploadHistory         │ │
│  │  • ProcessedData                                          │ │
│  └────────────────────────┬──────────────────────────────────┘ │
└───────────────────────────┼────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  PostgreSQL DATABASE                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Tables:                                                  │  │
│  │  • users            (authentication + roles)             │  │
│  │  • loan_data        (data pinjaman 10 juta+ rows)        │  │
│  │  • processed_data   (hasil olahan untuk dashboard)       │  │
│  │  • upload_history   (tracking uploads)                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 User Flow Diagram

### Flow 1: Login Process

```
User
  │
  ├─► Enter credentials (username/password)
  │
  ▼
Authentication System
  │
  ├─► Check credentials in database
  │
  ├──[Valid]──► Login user
  │            │
  │            ├─► Set session
  │            │
  │            ├─► Check user role (Admin/User)
  │            │
  │            └─► Redirect to Dashboard Home
  │
  └──[Invalid]─► Show error message
               │
               └─► Return to login page
```

### Flow 2: Admin Upload Data

```
Admin User
  │
  ├─► Navigate to "Upload Data" menu
  │
  ├─► Select file (.xlsx/.xls/.csv)
  │
  ├─► Submit form
  │
  ▼
Upload Handler
  │
  ├─► Validate file (size, format)
  │
  ├──[Invalid]──► Show error message
  │
  └──[Valid]────► Create UploadHistory record
                 │
                 ├─► Read file (Pandas)
                 │
                 ├─► Process each row
                 │   │
                 │   ├─► Validate data
                 │   │
                 │   ├─► Save to LoanData table
                 │   │
                 │   └─► Update success/fail count
                 │
                 ├─► Update UploadHistory status
                 │
                 └─► Show success message
                    │
                    └─► Redirect to Upload History
```

### Flow 3: View Dashboard

```
User (Admin/Regular)
  │
  ├─► Navigate to Dashboard menu
  │
  ▼
Dashboard View
  │
  ├─► Check user permissions
  │
  ├─► Query database
  │   │
  │   ├─► Get LoanData (dengan filter)
  │   │
  │   └─► Get ProcessedData (jika ada)
  │
  ├─► Process data
  │   │
  │   ├─► Aggregate data
  │   │
  │   ├─► Calculate metrics
  │   │
  │   └─► Prepare chart data
  │
  ├─► Render template
  │
  └─► Display dashboard
```

---

## 📊 Data Flow Diagram

### Upload ke Dashboard Flow

```
┌─────────────┐
│ Excel/CSV   │
│ File        │
└──────┬──────┘
       │
       │ Upload
       │
       ▼
┌─────────────────┐
│ File Validation │
│ • Size check    │
│ • Format check  │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐       ┌──────────────┐
│ Pandas Read     │──────►│ Raw Data     │
│ Excel/CSV       │       │ (DataFrame)  │
└─────────────────┘       └──────┬───────┘
                                 │
                                 │ Process
                                 │
                                 ▼
                          ┌──────────────┐
                          │ Validation   │
                          │ & Transform  │
                          └──────┬───────┘
                                 │
                                 ▼
                          ┌──────────────┐
                          │ Save to DB   │
                          │ (LoanData)   │
                          └──────┬───────┘
                                 │
                                 │
         ┌───────────────────────┼────────────────────┐
         │                       │                    │
         ▼                       ▼                    ▼
┌─────────────────┐    ┌─────────────────┐   ┌──────────────┐
│ Dashboard OS    │    │ Dashboard       │   │ Dashboard    │
│                 │    │ Summary         │   │ Grafik       │
│ Query & Display │    │                 │   │ Harian       │
│ • Outstanding   │    │ Query & Display │   │              │
│ • Metrics       │    │ • Medium Only   │   │ Query & Plot │
│ • Charts        │    │ • Konsol        │   │ • Daily      │
└─────────────────┘    │ • Only          │   │ • Trends     │
                       └─────────────────┘   └──────────────┘
```

---

## 🗂️ Struktur Direktori Detail

```
Performance Highlight SME Dashboard/
│
├── config/                          # Django Project Configuration
│   ├── __init__.py
│   ├── settings.py                  # Main settings (DB, Apps, etc)
│   ├── urls.py                      # Main URL routing
│   ├── wsgi.py                      # WSGI config for deployment
│   └── asgi.py                      # ASGI config for async
│
├── accounts/                        # User Management App
│   ├── migrations/                  # Database migrations
│   ├── management/
│   │   └── commands/
│   │       └── create_admin.py     # Custom command
│   ├── __init__.py
│   ├── models.py                   # User model (custom)
│   ├── views.py                    # Login/Logout views
│   ├── urls.py                     # accounts/ URLs
│   ├── admin.py                    # Admin config
│   └── apps.py
│
├── dashboard/                       # Dashboard App
│   ├── migrations/
│   ├── __init__.py
│   ├── models.py                   # LoanData, ProcessedData
│   ├── views.py                    # Dashboard views
│   ├── urls.py                     # dashboard/ URLs
│   ├── admin.py
│   └── apps.py
│
├── data_management/                 # Data Management App
│   ├── migrations/
│   ├── __init__.py
│   ├── models.py                   # UploadHistory
│   ├── views.py                    # Upload, History, Delete
│   ├── forms.py                    # Upload form
│   ├── utils.py                    # Processing utilities
│   ├── urls.py                     # data/ URLs
│   ├── admin.py
│   └── apps.py
│
├── templates/                       # HTML Templates
│   ├── base.html                   # Base template (sidebar, navbar)
│   ├── accounts/
│   │   └── login.html             # Login page
│   ├── dashboard/
│   │   ├── home.html              # Dashboard home
│   │   ├── dashboard_os.html      # Dashboard OS
│   │   ├── dashboard_summary.html # Dashboard Summary (tabs)
│   │   └── dashboard_grafik_harian.html
│   └── data_management/
│       ├── upload_data.html       # Upload form
│       ├── upload_history.html    # History table
│       └── delete_data.html       # Delete interface
│
├── static/                          # Static files (CSS, JS, Images)
│   └── (akan dibuat saat collectstatic)
│
├── media/                           # User uploaded files
│   └── uploads/
│       └── YYYY/MM/DD/             # Organized by date
│
├── venv/                            # Virtual environment
│   └── (Python packages)
│
├── manage.py                        # Django management script
├── requirements.txt                 # Python dependencies
├── .env                            # Environment variables (GITIGNORE)
├── .env.example                    # Template for .env
├── .gitignore                      # Git ignore rules
│
├── README.md                        # Main documentation
├── QUICKSTART.md                   # Quick setup guide
├── POSTGRESQL_TUTORIAL.md          # PostgreSQL setup
├── DEPLOYMENT.md                   # Production deployment
├── CHANGELOG.md                    # Version history
├── PROJECT_SUMMARY.md              # Project overview
├── ARCHITECTURE.md                 # This file
│
├── setup.ps1                       # PowerShell setup script
├── test_db_connection.py          # Test database connection
└── create_sample_data.py          # Generate sample data
```

---

## 🔐 Permission Matrix

| Feature | Admin | User |
|---------|-------|------|
| Login | ✅ | ✅ |
| View Dashboard Home | ✅ | ✅ |
| View Dashboard OS | ✅ | ✅ |
| View Dashboard Summary | ✅ | ✅ |
| View Dashboard Grafik Harian | ✅ | ✅ |
| Upload Data | ✅ | ❌ |
| View Upload History | ✅ | ❌ |
| Delete Data | ✅ | ❌ |
| Access Django Admin | ✅ | ❌ |

---

## 🗄️ Database Schema

### Table: users

```
┌──────────────┬──────────────┬─────────┬────────────┐
│ Column       │ Type         │ Null    │ Key        │
├──────────────┼──────────────┼─────────┼────────────┤
│ id           │ BigInt       │ NO      │ PRIMARY    │
│ username     │ Varchar(150) │ NO      │ UNIQUE     │
│ email        │ Varchar(254) │ YES     │            │
│ password     │ Varchar(128) │ NO      │            │
│ first_name   │ Varchar(150) │ YES     │            │
│ last_name    │ Varchar(150) │ YES     │            │
│ role         │ Varchar(10)  │ NO      │ INDEX      │
│ phone_number │ Varchar(15)  │ YES     │            │
│ is_active    │ Boolean      │ NO      │            │
│ is_staff     │ Boolean      │ NO      │            │
│ created_at   │ DateTime     │ NO      │            │
│ updated_at   │ DateTime     │ NO      │            │
└──────────────┴──────────────┴─────────┴────────────┘
```

### Table: loan_data

| Column                              | Type                | Null | Key     |
|-------------------------------------|---------------------|------|---------|
| id                                  | BigInt              | NO   | PRIMARY |
| periode                             | Varchar(30)         | NO   | INDEX   |
| kanca                               | Varchar(150)        | YES  |         |
| kode_uker                           | Varchar(50)         | YES  |         |
| uker                                | Varchar(150)        | YES  |         |
| ln_type                             | Varchar(50)         | YES  |         |
| nomor_rekening                      | Varchar(50)         | NO   | UNIQUE  |
| nama_debitur                        | Varchar(200)        | YES  |         |
| plafon                              | Decimal(18,2)       | YES  |         |
| next_pmt_date                       | Date                | YES  |         |
| next_int_pmt_date                   | Date                | YES  |         |
| rate                                | Decimal(7,4)        | YES  |         |
| tgl_menunggak                       | Date                | YES  |         |
| tgl_realisasi                       | Date                | YES  |         |
| tgl_jatuh_tempo                     | Date                | YES  |         |
| jangka_waktu                        | Integer             | YES  |         |
| flag_restruk                        | Varchar(50)         | YES  |         |
| cif_no                              | Varchar(50)         | NO   | INDEX   |
| kolektibilitas_lancar               | Varchar(50)         | YES  |         |
| kolektibilitas_dpk                  | Varchar(50)         | YES  |         |
| kolektibilitas_kurang_lancar        | Varchar(50)         | YES  |         |
| kolektibilitas_diragukan            | Varchar(50)         | YES  |         |
| kolektibilitas_macet                | Varchar(50)         | YES  |         |
| tunggakan_pokok                     | Decimal(18,2)       | YES  |         |
| tunggakan_bunga                     | Decimal(18,2)       | YES  |         |
| tunggakan_pinalti                   | Decimal(18,2)       | YES  |         |
| code                                | Varchar(50)         | YES  |         |
| description                         | Varchar(255)        | YES  |         |
| kol_adk                             | Varchar(50)         | YES  |         |
| pn_pengelola_singlepn               | Varchar(150)        | YES  |         |
| pn_pengelola_1                      | Varchar(150)        | YES  |         |
| pn_pemrakarsa                       | Varchar(150)        | YES  |         |
| pn_referral                         | Varchar(150)        | YES  |         |
| pn_restruk                          | Varchar(150)        | YES  |         |
| pn_pengelola_2                      | Varchar(150)        | YES  |         |
| pn_pemutus                          | Varchar(150)        | YES  |         |
| pn_crm                              | Varchar(150)        | YES  |         |
| pn_rm_referral_naik_segmentasi      | Varchar(150)        | YES  |         |
| pn_rm_crr                           | Varchar(150)        | YES  |         |
| created_at                          | DateTime            | NO   |         |
| updated_at                          | DateTime            | NO   |         |

Indexes:
- idx_periode_kanca (periode, kanca)
- idx_periode_kolektibilitas_macet (periode, kolektibilitas_macet)
- idx_nomor_rekening (nomor_rekening)

### Table: upload_history

```
┌────────────────┬──────────────┬─────────┬────────────┐
│ Column         │ Type         │ Null    │ Key        │
├────────────────┼──────────────┼─────────┼────────────┤
│ id             │ BigInt       │ NO      │ PRIMARY    │
│ uploaded_by_id │ BigInt       │ NO      │ FOREIGN    │
│ file_name      │ Varchar(255) │ NO      │            │
│ file_path      │ FileField    │ NO      │            │
│ file_size      │ BigInt       │ NO      │            │
│ total_rows     │ Integer      │ NO      │            │
│ successful_rows│ Integer      │ NO      │            │
│ failed_rows    │ Integer      │ NO      │            │
│ status         │ Varchar(20)  │ NO      │            │
│ error_log      │ Text         │ YES     │            │
│ notes          │ Text         │ YES     │            │
│ created_at     │ DateTime     │ NO      │ INDEX      │
│ completed_at   │ DateTime     │ YES     │            │
└────────────────┴──────────────┴─────────┴────────────┘
```

---

## 🔄 Request-Response Cycle

### Example: View Dashboard OS

```
1. User clicks "Dashboard OS" menu
   ↓
2. Browser sends GET request: /os/
   ↓
3. Django URL Router matches pattern
   ↓
4. Calls dashboard.views.dashboard_os_view()
   ↓
5. View function:
   - Checks user authentication (@login_required)
   - Queries LoanData from database
   - Processes data for metrics/charts
   - Prepares context dictionary
   ↓
6. Renders template: dashboard/dashboard_os.html
   ↓
7. Template engine:
   - Extends base.html
   - Inserts context data
   - Generates final HTML
   ↓
8. Django sends HTTP Response
   ↓
9. Browser receives HTML
   ↓
10. Browser renders page
    - Loads CSS (Bootstrap)
    - Loads JS (Chart.js)
    - Displays dashboard
```

---

## 📈 Scalability Considerations

### Current Capacity
- **Users**: Unlimited
- **Data Storage**: Depends on PostgreSQL config
- **Expected Load**: 10 juta+ records per tahun
- **Upload Size**: Max 100MB per file

### Optimization Strategies

1. **Database Level**
   - Proper indexing ✅
   - Partitioning (untuk data besar)
   - Connection pooling

2. **Application Level**
   - Query optimization
   - Caching (Redis)
   - Background tasks (Celery)

3. **Infrastructure Level**
   - Load balancing
   - CDN for static files
   - Database replication

---

**Document Version:** 1.0  
**Last Updated:** October 13, 2025  
**Created by:** BRI Development Team
