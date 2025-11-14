# Deployment Guide - Dashboard Performance Highlights SME

## 🚀 Production Deployment Checklist

### Pre-Deployment

- [ ] All features tested in development
- [ ] Database migrations reviewed
- [ ] Static files collected
- [ ] Environment variables configured
- [ ] SSL certificates ready (for HTTPS)
- [ ] Backup strategy in place
- [ ] Monitoring tools configured

### Environment Setup

#### 1. Server Requirements

**Minimum Specifications:**
- OS: Ubuntu 20.04 LTS / Windows Server 2019+
- RAM: 8GB
- CPU: 4 cores
- Storage: 100GB SSD
- PostgreSQL: 12+
- Python: 3.10+

**Recommended Specifications:**
- OS: Ubuntu 22.04 LTS
- RAM: 16GB
- CPU: 8 cores
- Storage: 500GB SSD (untuk data besar)
- PostgreSQL: 15+
- Python: 3.11+

#### 2. Install Dependencies (Ubuntu)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Install Nginx
sudo apt install nginx -y

# Install other dependencies
sudo apt install build-essential libpq-dev git -y
```

#### 3. Setup PostgreSQL

```bash
# Login sebagai postgres user
sudo -u postgres psql

# Buat database dan user
CREATE DATABASE sme_dashboard_prod;
CREATE USER sme_prod_user WITH PASSWORD 'strong_password_here';
ALTER ROLE sme_prod_user SET client_encoding TO 'utf8';
ALTER ROLE sme_prod_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE sme_prod_user SET timezone TO 'Asia/Jakarta';
GRANT ALL PRIVILEGES ON DATABASE sme_dashboard_prod TO sme_prod_user;

# Exit
\q
```

#### 4. Setup Application

```bash
# Create application directory
sudo mkdir -p /var/www/sme-dashboard
cd /var/www/sme-dashboard

# Clone repository (atau upload files)
# git clone <repository-url> .

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# Create .env file
nano .env
```

**.env for Production:**
```env
SECRET_KEY=your-very-long-random-secret-key-here-change-this-immediately
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-server-ip

DB_NAME=sme_dashboard_prod
DB_USER=sme_prod_user
DB_PASSWORD=strong_password_here
DB_HOST=localhost
DB_PORT=5432

# Optional: Email settings
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password
```

#### 5. Setup Django

```bash
# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Create admin user
python manage.py create_admin --username admin --email admin@bri.co.id --password ChangeThisPassword

# Test
python manage.py check --deploy
```

#### 6. Setup Gunicorn

Create systemd service file:

```bash
sudo nano /etc/systemd/system/sme-dashboard.service
```

**sme-dashboard.service:**
```ini
[Unit]
Description=SME Dashboard Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/sme-dashboard
Environment="PATH=/var/www/sme-dashboard/venv/bin"
ExecStart=/var/www/sme-dashboard/venv/bin/gunicorn \
    --workers 4 \
    --bind unix:/var/www/sme-dashboard/sme-dashboard.sock \
    --timeout 300 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    config.wsgi:application

[Install]
WantedBy=multi-user.target
```

Enable and start service:
```bash
sudo systemctl start sme-dashboard
sudo systemctl enable sme-dashboard
sudo systemctl status sme-dashboard
```

#### 7. Setup Nginx

```bash
sudo nano /etc/nginx/sites-available/sme-dashboard
```

**sme-dashboard nginx config:**
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 100M;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias /var/www/sme-dashboard/staticfiles/;
    }

    location /media/ {
        alias /var/www/sme-dashboard/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/sme-dashboard/sme-dashboard.sock;
        proxy_connect_timeout 300s;
        proxy_read_timeout 300s;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/sme-dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 8. Setup SSL with Let's Encrypt (Optional but Recommended)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal test
sudo certbot renew --dry-run
```

### Maintenance

#### Daily Backup Script

Create `/var/www/sme-dashboard/backup.sh`:

```bash
#!/bin/bash

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/sme-dashboard"
DB_NAME="sme_dashboard_prod"
DB_USER="sme_prod_user"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
PGPASSWORD='strong_password_here' pg_dump -U $DB_USER $DB_NAME | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Backup media files
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz /var/www/sme-dashboard/media/

# Delete old backups (keep 30 days)
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completed: $DATE"
```

Make executable and add to crontab:
```bash
chmod +x /var/www/sme-dashboard/backup.sh

# Add to crontab (daily at 2 AM)
sudo crontab -e
# Add line:
0 2 * * * /var/www/sme-dashboard/backup.sh >> /var/log/sme-backup.log 2>&1
```

#### Monitoring

Install monitoring tools:

```bash
# Install htop for system monitoring
sudo apt install htop -y

# Install PostgreSQL monitoring
sudo apt install postgresql-contrib -y

# Monitor logs
tail -f /var/log/nginx/error.log
journalctl -u sme-dashboard -f
tail -f /var/log/postgresql/postgresql-*.log
```

#### Update Deployment

```bash
cd /var/www/sme-dashboard

# Activate venv
source venv/bin/activate

# Pull changes (or upload new files)
# git pull origin main

# Install new dependencies (if any)
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart service
sudo systemctl restart sme-dashboard
sudo systemctl restart nginx
```

### Security Hardening

#### 1. Firewall

```bash
# Install ufw
sudo apt install ufw -y

# Allow SSH, HTTP, HTTPS, PostgreSQL
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw allow 5432/tcp  # PostgreSQL (dari internal only)

# Enable firewall
sudo ufw enable
```

#### 2. PostgreSQL Security

Edit `/etc/postgresql/15/main/pg_hba.conf`:
```
# Only allow local connections
local   all             postgres                                peer
local   all             all                                     peer
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
```

Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

#### 3. Django Security

In `settings.py`, ensure:

```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

### Performance Optimization

#### 1. Database Optimization

```sql
-- Create indexes
CREATE INDEX CONCURRENTLY idx_periode_kanca ON LW321(periode, kanca);
CREATE INDEX CONCURRENTLY idx_periode_kolektibilitas_macet ON LW321(periode, kolektibilitas_macet);
CREATE UNIQUE INDEX CONCURRENTLY idx_nomor_rekening ON LW321(nomor_rekening);
CREATE INDEX CONCURRENTLY idx_cif_no ON LW321(cif_no);

-- Vacuum and analyze
VACUUM ANALYZE;

-- Configure PostgreSQL
-- Edit /etc/postgresql/15/main/postgresql.conf
shared_buffers = 2GB
effective_cache_size = 6GB
maintenance_work_mem = 512MB
work_mem = 16MB
```

#### 2. Gunicorn Workers

Calculate optimal workers:
```
workers = (2 x CPU cores) + 1
```

For 4 core server:
```
workers = (2 x 4) + 1 = 9 workers
```

#### 3. Caching (Redis)

```bash
# Install Redis
sudo apt install redis-server -y

# Install Python Redis
pip install django-redis
```

Add to `settings.py`:
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### Troubleshooting Production

#### Application not accessible

```bash
# Check gunicorn status
sudo systemctl status sme-dashboard

# Check nginx status
sudo systemctl status nginx

# Check logs
journalctl -u sme-dashboard -n 50
tail -f /var/log/nginx/error.log
```

#### Database connection issues

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection
psql -U sme_prod_user -d sme_dashboard_prod -h localhost
```

#### High CPU/Memory usage

```bash
# Monitor processes
htop

# Check PostgreSQL queries
psql -U postgres -d sme_dashboard_prod
SELECT * FROM pg_stat_activity;
```

---

**Deployment Guide Version:** 1.0  
**Last Updated:** October 13, 2025
