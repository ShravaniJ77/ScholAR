@echo off
REM ScholAR - Windows Launcher (Updated)

echo ======================================
echo   ScholAR - Autonomous Research Agent
echo ======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo + %PYTHON_VERSION%
echo.

REM Install/update dependencies
echo Checking dependencies...
python -m pip install -q -r requirements.txt
if errorlevel 1 (
    echo - Failed to install dependencies
    exit /b 1
)
echo + Dependencies ready
echo.

REM Run the app from app subdirectory
echo.
echo Launching ScholAR...
echo Open browser to: http://localhost:8501
echo.
python -m streamlit run app/streamlit_app.py --server.port 8501 --server.address 127.0.0.1 --logger.level=error

pause

