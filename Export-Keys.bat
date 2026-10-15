@echo off
title BT-DualBoot Tools - Windows Key Exporter
cd /d "%~dp0"

echo ========================================================
echo    BT-DualBoot Tools: Windows Bluetooth Key Exporter
echo ========================================================
echo.

net session >nul 2>&1
if %errorLevel% == 0 (
    powershell -NoProfile -ExecutionPolicy Bypass -File "windows\Export-BluetoothKeys.ps1"
) else (
    echo [*] Yonetici haklari ile baslatiliyor (UAC onayi veriniz)...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process powershell -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File \"\"%~dp0windows\Export-BluetoothKeys.ps1\"\"' -Verb RunAs"
)

echo.
echo ========================================================
echo [BILGI] Export tamamlandiktan sonra olusan btkeys.json
echo dosyasini Linux ortamina tasiyiniz.
echo ========================================================
echo.
pause
