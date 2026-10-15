# Export-BluetoothKeys.ps1
# Part of BT-DualBoot Tools (v1.0 - Classic Bluetooth)
#
# Description: Safely exports Classic Bluetooth pairing keys from the Windows registry
#              to a JSON file (btkeys.json) for easy syncing with Linux (BlueZ).
#
# Requirements: Must be run in PowerShell as Administrator (uses a temporary SYSTEM scheduled task).

[CmdletBinding()]
param(
    [string]$OutputPath = (Join-Path (Get-Location) "btkeys.json")
)

$ErrorActionPreference = "Stop"

# 1. Verify Elevated Privileges
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "`n[ERROR] Administrator privileges are required to access Bluetooth keys." -ForegroundColor Red
    Write-Host "Please right-click PowerShell and choose 'Run as Administrator'.`n" -ForegroundColor Yellow
    Exit 1
}

# Helper: Friendly Name Resolution
function Get-DeviceFriendlyName {
    param([string]$deviceMacRaw) # 12 characters, e.g. "54466b0009fb"
    $cleanMac = $deviceMacRaw.Replace(":", "").ToLower()
    $formattedMac = ($cleanMac -replace '..(?!$)', '$0:').ToUpper()
    
    # Check BTHPORT Devices registry parameter
    $regPath = "HKLM:\SYSTEM\CurrentControlSet\Services\BTHPORT\Parameters\Devices\$cleanMac"
    if (Test-Path $regPath) {
        $nameBytes = (Get-ItemProperty $regPath -ErrorAction SilentlyContinue).Name
        if ($nameBytes) {
            try {
                $name = [System.Text.Encoding]::UTF8.GetString($nameBytes).Trim([char]0)
                if ($name -and $name -match '^[a-zA-Z0-9_\-\s\(\)\.\,\&\+@!#%]+$') {
                    return $name
                }
            } catch {}
        }
    }
    
    # Fallback to PnP Device cache
    try {
        $pnp = Get-PnpDevice -Class "Bluetooth" -ErrorAction SilentlyContinue | 
            Where-Object { $_.DeviceID -like "*$cleanMac*" -or $_.InstanceId -like "*$cleanMac*" } | 
            Select-Object -First 1
        if ($pnp -and $pnp.FriendlyName) {
            return $pnp.FriendlyName
        }
    } catch {}
    
    return "Unknown Device ($formattedMac)"
}

# 2. Setup Ephemeral Task and Output File
$tempRegFile = Join-Path $env:TEMP "btkeys_temp_$(Get-Random).reg"
$taskName = "BTDualBoot_ExportKeys_$(Get-Random)"

Write-Host "`n========================================================" -ForegroundColor Cyan
Write-Host "          BT-DualBoot Tools: Windows Key Exporter       " -ForegroundColor Cyan
Write-Host "========================================================`n" -ForegroundColor Cyan

Write-Host "[*] Registering temporary SYSTEM task..." -ForegroundColor DarkGray
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c reg export HKLM\SYSTEM\CurrentControlSet\Services\BTHPORT\Parameters\Keys `"$tempRegFile`" /y"
$principal = New-ScheduledTaskPrincipal -UserId "NT AUTHORITY\SYSTEM" -LogonType ServiceAccount
$settings = New-ScheduledTaskSettingsSet

Register-ScheduledTask -TaskName $taskName -Action $action -Principal $principal -Settings $settings -Force | Out-Null

try {
    Write-Host "[*] Executing registry extraction via NT AUTHORITY\SYSTEM..." -ForegroundColor Cyan
    Start-ScheduledTask -TaskName $taskName
    
    $timeoutSeconds = 12
    $elapsed = 0
    $success = $false
    
    while ($elapsed -lt $timeoutSeconds) {
        $task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
        if ($task -and $task.State -ne "Running") {
            $success = $true
            break
        }
        Start-Sleep -Seconds 1
        $elapsed++
    }
    
    if (-not $success -or -not (Test-Path $tempRegFile) -or (Get-Item $tempRegFile).Length -eq 0) {
        throw "Failed to extract Bluetooth keys. The scheduled task timed out or produced an empty file."
    }

    # 3. Parse Registry Export in Memory
    Write-Host "[*] Parsing Bluetooth adapters and paired devices..." -ForegroundColor Cyan
    $rawLines = Get-Content $tempRegFile -Encoding Unicode
    
    # Handle multi-line continuations in .reg format
    $lines = @()
    $currentLine = ""
    foreach ($l in $rawLines) {
        $trimmed = $l.Trim()
        if ($trimmed.EndsWith("\")) {
            $currentLine += $trimmed.Substring(0, $trimmed.Length - 1)
        } else {
            $currentLine += $trimmed
            $lines += $currentLine
            $currentLine = ""
        }
    }
    if ($currentLine -ne "") { $lines += $currentLine }

    $adapters = @{}
    $currentAdapter = $null
    $currentBleDevice = $null

    foreach ($line in $lines) {
        if ([string]::IsNullOrWhiteSpace($line) -or $line.StartsWith(";")) { continue }

        if ($line.StartsWith("[") -and $line.EndsWith("]")) {
            $keyPath = $line.Substring(1, $line.Length - 2)
            
            # 1. Adapter key: HKLM\...\Keys\<12-hex-mac>
            if ($keyPath -match "BTHPORT\\Parameters\\Keys\\(?<adapterRaw>[0-9a-fA-F]{12})$") {
                $adapterMacRaw = $Matches['adapterRaw'].ToUpper()
                $adapterMacFormatted = ($adapterMacRaw -replace '..(?!$)', '$0:').ToUpper()
                $currentAdapter = $adapterMacRaw
                $currentBleDevice = $null
                
                if (-not $adapters.ContainsKey($currentAdapter)) {
                    $adapters[$currentAdapter] = [ordered]@{
                        adapter = $adapterMacFormatted
                        devices = @()
                    }
                }
            } 
            # 2. BLE Device subkey: HKLM\...\Keys\<adapterRaw>\<deviceRaw>
            elseif ($keyPath -match "BTHPORT\\Parameters\\Keys\\(?<adapterRaw>[0-9a-fA-F]{12})\\(?<deviceRaw>[0-9a-fA-F]{12})$") {
                $adapterMacRaw = $Matches['adapterRaw'].ToUpper()
                $adapterMacFormatted = ($adapterMacRaw -replace '..(?!$)', '$0:').ToUpper()
                $deviceMacRaw = $Matches['deviceRaw'].ToUpper()
                $deviceMacFormatted = ($deviceMacRaw -replace '..(?!$)', '$0:').ToUpper()
                
                $currentAdapter = $adapterMacRaw
                $currentBleDevice = $deviceMacFormatted
                
                if (-not $adapters.ContainsKey($currentAdapter)) {
                    $adapters[$currentAdapter] = [ordered]@{
                        adapter = $adapterMacFormatted
                        devices = @()
                    }
                }
                
                $existing = $adapters[$currentAdapter].devices | Where-Object { $_.mac -eq $deviceMacFormatted } | Select-Object -First 1
                if (-not $existing) {
                    $deviceName = Get-DeviceFriendlyName $deviceMacRaw
                    $newDev = [ordered]@{
                        mac  = $deviceMacFormatted
                        name = $deviceName
                        key  = ""
                        ble  = [ordered]@{}
                    }
                    $adapters[$currentAdapter].devices += $newDev
                }
            } else {
                $currentAdapter = $null
                $currentBleDevice = $null
            }
        } elseif ($line -match '^"([^"]+)"\s*=\s*(.+)$') {
            $valName = $Matches[1]
            $valVal = $Matches[2]
            
            # Classic Device Link Key
            if ($currentAdapter -and (-not $currentBleDevice) -and $valName -match "^[0-9a-fA-F]{12}$") {
                $deviceMacRaw = $valName.ToUpper()
                $deviceMacFormatted = ($deviceMacRaw -replace '..(?!$)', '$0:').ToUpper()
                
                $keyHex = ""
                if ($valVal.StartsWith("hex:")) {
                    $keyHex = $valVal.Substring(4).Replace(",", "").Replace(" ", "").ToUpper()
                }
                
                $existing = $adapters[$currentAdapter].devices | Where-Object { $_.mac -eq $deviceMacFormatted } | Select-Object -First 1
                if ($existing) {
                    $existing.key = $keyHex
                } else {
                    $deviceName = Get-DeviceFriendlyName $deviceMacRaw
                    $deviceObj = [ordered]@{
                        mac  = $deviceMacFormatted
                        name = $deviceName
                        key  = $keyHex
                    }
                    $adapters[$currentAdapter].devices += $deviceObj
                }
            }
            # BLE Properties: LTK, ERand, EDIV
            elseif ($currentAdapter -and $currentBleDevice) {
                $devObj = $adapters[$currentAdapter].devices | Where-Object { $_.mac -eq $currentBleDevice } | Select-Object -First 1
                if ($devObj) {
                    if (-not $devObj.Contains("ble") -or -not $devObj.ble) {
                        $devObj["ble"] = [ordered]@{}
                    }
                    if ($valName -eq "LTK" -and $valVal.StartsWith("hex:")) {
                        $devObj.ble["ltk"] = $valVal.Substring(4).Replace(",", "").Replace(" ", "").ToUpper()
                    } elseif ($valName -eq "ERand" -and $valVal -match "hex(\([0-9a-fA-F]+\))?:(.+)$") {
                        $rawHex = $Matches[2].Replace(",", "").Replace(" ", "").ToUpper()
                        $devObj.ble["erand"] = $rawHex
                    } elseif ($valName -eq "EDIV" -and $valVal.StartsWith("dword:")) {
                        $devObj.ble["ediv"] = [Convert]::ToInt32($valVal.Substring(6), 16)
                    }
                }
            }
        }
    }

    # 4. Generate Output JSON
    $adaptersList = @()
    foreach ($key in $adapters.Keys) {
        if ($adapters[$key].devices.Count -gt 0) {
            $adaptersList += $adapters[$key]
        }
    }

    if ($adaptersList.Count -eq 0) {
        Write-Host "`n[WARNING] No Classic Bluetooth paired devices found in registry.`n" -ForegroundColor Yellow
        Exit 0
    }

    $jsonContent = ConvertTo-Json -InputObject $adaptersList -Depth 10
    Set-Content -Path $OutputPath -Value $jsonContent -Encoding UTF8

    Write-Host "`n========================================================================" -ForegroundColor Green
    Write-Host "  KEY TEBRIKLER! BLUETOOTH ANAHTAR PAKETINIZ HAZIR (btkeys.json)" -ForegroundColor Green
    Write-Host "========================================================================`n" -ForegroundColor Green
    Write-Host "  Oluşturulan Dosya: $OutputPath`n" -ForegroundColor Cyan

    foreach ($adapterObj in $adaptersList) {
        Write-Host "  * Adapter: $($adapterObj.adapter)" -ForegroundColor Cyan
        foreach ($device in $adapterObj.devices) {
            Write-Host "     |-- Cihaz: $($device.name)" -ForegroundColor White
            Write-Host "     |   MAC:   $($device.mac)" -ForegroundColor DarkGray
            if ($device.key) {
                Write-Host "     |   Classic Key: $($device.key.Substring(0, 4))...$($device.key.Substring($device.key.Length - 4))" -ForegroundColor Green
            }
            if ($device.ble -and $device.ble.ltk) {
                Write-Host "     |   BLE LTK:     $($device.ble.ltk.Substring(0, 4))...$($device.ble.ltk.Substring($device.ble.ltk.Length - 4))" -ForegroundColor Yellow
            }
        }
        Write-Host ""
    }

    Write-Host "========================================================================" -ForegroundColor Yellow
    Write-Host "  👉 SIRADAKI ADIM:" -ForegroundColor Yellow
    Write-Host "  1. Bu klasordeki 'btkeys.json' dosyasini bir USB Flash Bellege atin" -ForegroundColor White
    Write-Host "     (veya Linux'tan erisebildiginiz bir ortak klasore kopyalayin)." -ForegroundColor White
    Write-Host "  2. Bilgisayarinizi yeniden baslatip LINUX'a gecin." -ForegroundColor White
    Write-Host "  3. Linux terminalinde su komutu calistirin:" -ForegroundColor White
    Write-Host "        sudo python sync.py" -ForegroundColor Cyan
    Write-Host "     (Dosyayi bulamazsa fareyle terminale surukleyip birakabilirsiniz!)" -ForegroundColor DarkGray
    Write-Host "========================================================================`n" -ForegroundColor Yellow

} finally {
    # 6. Guaranteed Cleanup of Task and Temporary Files
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue | Out-Null
    if (Test-Path $tempRegFile) {
        Remove-Item $tempRegFile -Force -ErrorAction SilentlyContinue
    }
}
