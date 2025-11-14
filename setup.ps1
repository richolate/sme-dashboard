# Setup Script untuk Dashboard Performance Highlights SME
# Run dengan: .\setup.ps1

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Dashboard Performance Highlights SME - Setup Script" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "[1/8] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python not found! Please install Python 3.10+" -ForegroundColor Red
    exit 1
}

# Check if venv exists
Write-Host "[2/8] Setting up Virtual Environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "  ✓ Virtual environment already exists" -ForegroundColor Green
} else {
    Write-Host "  Creating virtual environment..." -ForegroundColor White
    python -m venv venv
    Write-Host "  ✓ Virtual environment created" -ForegroundColor Green
}

# Activate venv
Write-Host "[3/8] Activating Virtual Environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "  ✓ Virtual environment activated" -ForegroundColor Green

# Install dependencies
Write-Host "[4/8] Installing dependencies..." -ForegroundColor Yellow
pip install -q --upgrade pip
pip install -q -r requirements.txt
Write-Host "  ✓ Dependencies installed" -ForegroundColor Green

# Check .env file
Write-Host "[5/8] Checking environment configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "  ✓ .env file exists" -ForegroundColor Green
} else {
    Write-Host "  Creating .env from template..." -ForegroundColor White
    Copy-Item ".env.example" ".env"
    Write-Host "  ✓ .env file created" -ForegroundColor Green
    Write-Host "  ⚠ Please edit .env file with your database credentials!" -ForegroundColor Yellow
}

# Test database connection
Write-Host "[6/8] Testing database connection..." -ForegroundColor Yellow
try {
    $dbTest = python test_db_connection.py 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Database connection successful" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Database connection failed" -ForegroundColor Red
        Write-Host "  Please check your .env configuration" -ForegroundColor Yellow
        Write-Host "  Make sure PostgreSQL is running and database exists" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ⚠ Could not test database (might be first run)" -ForegroundColor Yellow
}

# Run migrations
Write-Host "[7/8] Running database migrations..." -ForegroundColor Yellow
python manage.py makemigrations --noinput
python manage.py migrate --noinput
Write-Host "  ✓ Migrations completed" -ForegroundColor Green

# Ask to create admin user
Write-Host "[8/8] Creating admin user..." -ForegroundColor Yellow
$createAdmin = Read-Host "Create admin user? (y/n)"
if ($createAdmin -eq "y" -or $createAdmin -eq "Y") {
    python manage.py create_admin
    Write-Host "  ✓ Admin user created" -ForegroundColor Green
} else {
    Write-Host "  Skipped admin user creation" -ForegroundColor Yellow
}

# Final messages
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Edit .env file with your database credentials" -ForegroundColor White
Write-Host "2. Run: python manage.py runserver" -ForegroundColor White
Write-Host "3. Open browser: http://127.0.0.1:8000" -ForegroundColor White
Write-Host "4. Login with: admin / admin123 (change password!)" -ForegroundColor White
Write-Host ""
Write-Host "Documentation:" -ForegroundColor Yellow
Write-Host "- README.md - Complete documentation" -ForegroundColor White
Write-Host "- QUICKSTART.md - Quick start guide" -ForegroundColor White
Write-Host "- POSTGRESQL_TUTORIAL.md - PostgreSQL setup" -ForegroundColor White
Write-Host ""
Write-Host "Happy coding! 🚀" -ForegroundColor Cyan
Write-Host ""
