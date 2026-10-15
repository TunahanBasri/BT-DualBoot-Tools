@echo off
title BT-DualBoot Tools - Windows Key Exporter
cd /d "%~dp0"

echo ========================================================
echo    BT-DualBoot Tools: Windows Bluetooth Key Exporter
echo ========================================================
echo.

net session >nul 2>&1
if %errorLevel% == 0 (
    powershell -NoProfile -ExecutionPolicy Bypass -File "Export-BluetoothKeys.ps1"
) else (
    echo [*] Yonetici haklari ile baslatiliyor (UAC onayi veriniz)...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process powershell -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File \"\"%~dp0Export-BluetoothKeys.ps1\"\"' -Verb RunAs"
)

echo.
pause
