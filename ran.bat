@echo off
:: Check if local virtual environment Python exists directly (e.g. Conda style)
if exist "%~dp0venv\python.exe" (
    echo [INFO] Found local Python env. Running with venv/python.exe...
    "%~dp0venv\python.exe" "%~dp0run.py"
) else if exist "%~dp0venv\Scripts\activate.bat" (
    echo [INFO] Found standard venv. Activating...
    call "%~dp0venv\Scripts\activate.bat"
    python "%~dp0run.py"
) else (
    echo [WARNING] Virtual environment 'venv' not found. Running with global python...
    python "%~dp0run.py"
)