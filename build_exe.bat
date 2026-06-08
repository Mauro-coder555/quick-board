@echo off
setlocal

echo.
echo ======================================
echo  quick-board Windows build
echo ======================================
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0build_exe.ps1"

echo.
pause