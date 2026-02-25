<#
.SYNOPSIS
    Starts the BrosDen-AV Django App.
    Provides an interactive menu to choose between Waitress (WSGI), Uvicorn (ASGI), or Django Dev Server.
#>

$ErrorActionPreference = "Stop"

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "=========================================="
Write-Host " BrosDen-AV Server Launcher"
Write-Host "==========================================`n"

# Ensure venv exists and activate
if (!(Test-Path ".\.venv")) {
    Write-Host "Error: .venv not found. Please create it first." -ForegroundColor Red
    exit 1
}

if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    . .\.venv\Scripts\Activate.ps1
}

$port = 8000

Write-Host "Choose a server:"
Write-Host "1. Waitress (WSGI - Production Windows)"
Write-Host "2. Uvicorn (ASGI - Fast async handling)"
Write-Host "3. Django Dev Server (Default python manage.py runserver)"
Write-Host "4. Exit"

$choice = Read-Host "`nEnter your choice (1-4)"

switch ($choice) {
    '1' {
        Write-Host "`nStarting Waitress server on port $port... Access via http://localhost:$port"
        waitress-serve --port=$port config.wsgi:application
    }
    '2' {
        Write-Host "`nStarting Uvicorn server on port $port... Access via http://localhost:$port"
        uvicorn config.asgi:application --host 0.0.0.0 --port $port
    }
    '3' {
        Write-Host "`nStarting Django Development server..."
        python manage.py runserver
    }
    Default {
        Write-Host "Exiting. No server started."
    }
}
