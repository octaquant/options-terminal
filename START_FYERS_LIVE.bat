@echo off
title OCTAQUANT - FYERS Data Connector
cd /d "%~dp0"
py -3 -m pip install -r requirements.txt
if errorlevel 1 (
  echo Dependency installation failed. Check Python and internet connection.
  pause
  exit /b 1
)
py -3 -m streamlit run fyers_live.py
pause
