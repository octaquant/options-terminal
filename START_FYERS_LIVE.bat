@echo off
title OCTAQUANT - FYERS Data Connector
cd /d "%~dp0"

echo Checking Python 3.12...
py -3.12 --version
if errorlevel 1 (
  echo Python 3.12 was not found. Install it with:
  echo winget install -e --id Python.Python.3.12 --scope user
  pause
  exit /b 1
)

echo.
echo Upgrading pip...
py -3.12 -m pip install --upgrade pip
if errorlevel 1 (
  echo pip upgrade failed.
  pause
  exit /b 1
)

echo.
echo Installing OCTAQUANT dependencies directly...
echo This avoids any local requirements.txt formatting issue.
py -3.12 -m pip install "streamlit>=1.36,<2.0" "pandas>=2.0,<3.0" fyers-apiv3
if errorlevel 1 (
  echo.
  echo Dependency installation failed. Send a screenshot of this window.
  pause
  exit /b 1
)

echo.
echo Starting OCTAQUANT FYERS connector...
py -3.12 -m streamlit run fyers_live.py
pause
