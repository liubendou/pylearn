@echo off
cd /d "%~dp0"
set PY=C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe
if not exist "%PY%" set PY=python
"%PY%" learn_python.py
if errorlevel 1 (
  echo.
  echo Failed to start. See the error above.
  pause
)
