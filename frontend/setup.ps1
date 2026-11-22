# ExamVault Frontend Setup Script
# Run from the frontend/ directory

Write-Host "=== ExamVault Frontend Setup ===" -ForegroundColor Cyan

# Create .env.local for Vite
if (-not (Test-Path ".env.local")) {
    @"
# API base URL — leave as /api to use Vite proxy to localhost:5000
VITE_API_URL=
"@ | Out-File -Encoding utf8 ".env.local"
    Write-Host "[1/3] .env.local created" -ForegroundColor Green
}

# Install npm packages
Write-Host "[2/3] Installing npm packages..." -ForegroundColor Cyan
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: npm install failed. Is Node.js installed?" -ForegroundColor Red
    exit 1
}

Write-Host "[3/3] Done!" -ForegroundColor Green
Write-Host ""
Write-Host "=== Start development server ===" -ForegroundColor Cyan
Write-Host "npm run dev"
Write-Host ""
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Green
Write-Host "Make sure Flask backend is running on http://localhost:5000" -ForegroundColor Yellow
