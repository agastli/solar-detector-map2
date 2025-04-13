@echo off
title ☀️ Solar Detector Setup & Launcher
echo --------------------------------------------------
echo 🚀 Setting up Solar Detector App...
echo --------------------------------------------------

REM Step 1: Check Python
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo ❌ Python is not installed. Please install Python 3.8+ and try again.
    pause
    exit /b
)

REM Step 2: Create venv
IF NOT EXIST venv (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Step 3: Activate venv
call venv\Scripts\activate.bat

REM Step 4: Upgrade pip
echo 🔄 Upgrading pip...
python -m pip install --upgrade pip

REM Step 5: Install pip-tools (for pip-compile if needed later)
pip install pip-tools

REM Step 6: Install packages from requirements.txt
IF EXIST requirements.txt (
    echo 📥 Installing packages from requirements.txt...
    pip install --require-hashes -r requirements.txt
) ELSE (
    echo ⚠️ requirements.txt not found. Creating from requirements.in...
    pip-compile requirements.in --generate-hashes --allow-unsafe
    pip install --require-hashes -r requirements.txt
)

REM Step 7: Launch the app
echo ✅ All done. Launching the Streamlit app...
python -m streamlit run app/main.py

pause
