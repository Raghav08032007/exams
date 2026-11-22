# ExamVault Backend Setup Script
# Run this from the backend/ directory in PowerShell

Write-Host "=== ExamVault Backend Setup ===" -ForegroundColor Cyan

# Step 1: Copy .env
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "[1/5] .env created from .env.example" -ForegroundColor Green
    Write-Host "      Edit .env if you need to customize MySQL credentials" -ForegroundColor Yellow
} else {
    Write-Host "[1/5] .env already exists, skipping" -ForegroundColor Yellow
}

# Define Python path
if (Test-Path ".\venv\Scripts\python.exe") {
    $PYTHON = ".\venv\Scripts\python.exe"
} else {
    $PYTHON = "python"
}

# Step 2: Install dependencies
Write-Host "[2/5] Installing Python dependencies..." -ForegroundColor Cyan
& $PYTHON -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: pip install failed." -ForegroundColor Red
    exit 1
}

# Step 3: Initialize Database Schema
Write-Host "[3/5] Initializing database and ensuring tables exist..." -ForegroundColor Cyan
& $PYTHON init_db.py
& $PYTHON -c "from app import create_app; create_app()"
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Database initialization failed. Check MySQL connection in .env" -ForegroundColor Red
    exit 1
}

# Step 4: Run Schema Migrations (Textbooks, Interactive Features, Syllabus, Classifications)
Write-Host "[4/5] Running schema migrations & indexers..." -ForegroundColor Cyan
if (Test-Path "scripts\migrate_textbooks_schema.py") {
    & $PYTHON scripts\migrate_textbooks_schema.py
}
if (Test-Path "scripts\migrate_interactive_features.py") {
    & $PYTHON scripts\migrate_interactive_features.py
}
if (Test-Path "scripts\migrate_syllabus_schema.py") {
    & $PYTHON scripts\migrate_syllabus_schema.py
}
if (Test-Path "scripts\classify_and_migrate_papers.py") {
    & $PYTHON scripts\classify_and_migrate_papers.py
}

# Step 5: Verify Setup
Write-Host "[5/5] Verifying API endpoints and database integrity..." -ForegroundColor Cyan
& $PYTHON -c "from app import create_app; from app.db import get_db; app = create_app(); ctx = app.app_context(); ctx.push(); conn = get_db(); cur = conn.cursor(); cur.execute('SELECT COUNT(*) as cnt FROM papers WHERE verification_status = \"verified\"'); p_cnt = cur.fetchone()['cnt']; cur.execute('SELECT COUNT(*) as cnt FROM textbooks'); tb_cnt = cur.fetchone()['cnt']; print(f'Ready! Verified Papers: {p_cnt} | Textbooks: {tb_cnt}')"

Write-Host ""
Write-Host "=== Setup Complete! ===" -ForegroundColor Green
Write-Host "Start the server with: .\venv\Scripts\python.exe run.py" -ForegroundColor Cyan
Write-Host "API health check:      http://localhost:5000/health" -ForegroundColor Cyan
Write-Host "Sources & Provenance:  http://localhost:5000/sources/" -ForegroundColor Cyan
