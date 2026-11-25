@echo off
cd /d "%~dp0"
set PY=C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe
if not exist "%PY%" set PY=python
"%PY%" jizhang.py
echo.
pause
