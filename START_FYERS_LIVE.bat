@echo off
title OCTAQUANT - FYERS Data Connector
cd /d "%~dp0"

REM FYERS SDK dependency aiohttp may require a C++ compiler on Python 3.14.
REM Use Python 3.12, for which compatible Windows wheels are available.
py -3.12 --version >nul 2>&1
if errorlevel 1 (
  echo Python 3.12 was not found.
  echo Install Python 3.12 x64 from https://www.python.org/downloads/release/python-31210/
  echo During setup, select Add Python to PATH and Install py launcher.
  pause
  exit /b 1
)

py -3.12 -m pip install --upgrade pip
py -3.12 -m pip install -r requirements.txt
if errorlevel 1 (
  echo Dependency installation failed. Please send a screenshot of the LAST 20 lines.
  pause
  exit /b 1
)
py -3.12 -m streamlit run fyers_live.py
pause
