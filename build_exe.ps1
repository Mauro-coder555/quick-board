$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "======================================"
Write-Host " quick-board Windows build"
Write-Host "======================================"
Write-Host ""

if (-Not (Test-Path ".\main.py")) {
    Write-Host "Error: this script must be executed from the project root."
    exit 1
}

if (-Not (Test-Path ".\.venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}

Write-Host "Activating virtual environment..."
& .\.venv\Scripts\Activate.ps1

Write-Host "Upgrading pip..."
python -m pip install --upgrade pip

Write-Host "Installing app dependencies..."
pip install -r requirements.txt


Write-Host "Cleaning previous builds..."
if (Test-Path ".\build") {
    Remove-Item ".\build" -Recurse -Force
}

if (Test-Path ".\dist") {
    Remove-Item ".\dist" -Recurse -Force
}

if (Test-Path ".\quick-board.spec") {
    Remove-Item ".\quick-board.spec" -Force
}

Write-Host "Building executable..."
pyinstaller `
    --noconfirm `
    --onefile `
    --windowed `
    --name quick-board `
    main.py

Write-Host ""
Write-Host "Build completed successfully."
Write-Host ""
Write-Host "Executable created at:"
Write-Host "dist\quick-board.exe"
Write-Host ""