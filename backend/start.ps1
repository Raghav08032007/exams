# Start the ExamVault backend server
Write-Host "Starting ExamVault Backend..." -ForegroundColor Cyan

if (Test-Path ".\venv\Scripts\python.exe") {
    $PYTHON = ".\venv\Scripts\python.exe"
} else {
    $PYTHON = "python"
}

& $PYTHON run.py

