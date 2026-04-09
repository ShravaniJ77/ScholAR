@echo off
REM ScholAR Startup Script (Windows)

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

REM Install requirements
echo Checking dependencies...
python -c "import streamlit; import pandas; import plotly; import networkx" >nul 2>&1

if errorlevel 1 (
    echo Installing dependencies...
    pip install -q -r requirements.txt
    if errorlevel 1 (
        echo - Failed to install dependencies
        exit /b 1
    )
    echo + Dependencies installed
) else (
    echo + All dependencies found
)

echo.
echo Launching ScholAR...
echo Opening: http://localhost:8501
echo.
echo Press Ctrl+C to stop
echo.

REM Run Streamlit app
streamlit run streamlit_app.py

pause
