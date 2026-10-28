@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0construir.ps1" %*
pause
