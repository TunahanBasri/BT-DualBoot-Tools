# Export-BluetoothKeys.ps1
# Part of BT DualBoot Tools
#
# Description: Exports Bluetooth pairing keys (Classic and BLE) from the Windows registry
#              to a JSON file (btkeys.json) for easy syncing with Linux (BlueZ).
#
# Requirements: Must be run as Administrator (uses a temporary SYSTEM scheduled task).

$ErrorActionPreference = "Stop"

# 1. Check Administrator Privileges
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[ERROR] This script must be run as an Administrator. Please run PowerShell as Administrator." -ForegroundColor Red
    Exit 1
}

# Helper: Convert ERand (little-endian hex) to Rand (decimal integer string) for BlueZ
function Convert-ERandToRand {
    param([string]$eRandHex) # e.g. "E03ADB0BA8551C36"
    if ([string]::IsNullOrEmpty($eRandHex) -or $eRandHex.Length -ne 16) {
        return "0"
    }
    # Reverse byte order (little-endian to big-endian)
    $reversedHex = ""
    for ($i = 14; $i -ge 0; $i -= 2) {
        $reversedHex += $eRandHex.Substring($i, 2)
    }
    try {
        # Convert big-endian hex to unsigned 64-bit integer string
        return [System.Convert]::ToUInt64($reversedHex, 16).ToString()
    } catch {
        return "0"
    }
}

# Helper: Get Friendly Name of Device from Registry or system
function Get-DeviceFriendlyName {
    param([string]$deviceMacRaw) # e.g. "54466b0009fb"
    $cleanMac = $deviceMacRaw.Replace(":", "").ToLower()
    $formattedMac = ($cleanMac -replace '..(?!$)', '$0:').ToUpper()
    
    # 1. Try reading the friendly name from the BTHPORT Devices registry key
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
    
    # 2. Try falling back to Get-PnpDevice
    try {
        $pnpDevice = Get-PnpDevice -Class "Bluetooth" -ErrorAction SilentlyContinue | 
            Where-Object { $_.DeviceID -like "*$cleanMac*" -or $_.InstanceId -like "*$cleanMac*" } | 
            Select-Object -First 1
        if ($pnpDevice -and $pnpDevice.FriendlyName) {
            return $pnpDevice.FriendlyName
        }
    } catch {}
    
    return "Unknown Device ($formattedMac)"
}

# 2. Set Up Temporary Files and Tasks
$tempRegFile = Join-Path $env:TEMP "btkeys_temp.reg"
if (Test-Path $tempRegFile) { Remove-Item $tempRegFile -Force }

$taskName = "ExportBluetoothKeysTemp"
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c reg export HKLM\SYSTEM\CurrentControlSet\Services\BTHPORT\Parameters\Keys `"$tempRegFile`" /y"
$principal = New-ScheduledTaskPrincipal -UserId "NT AUTHORITY\SYSTEM" -LogonType ServiceAccount
$settings = New-ScheduledTaskSettingsSet

Write-Host "[*] Registering temporary SYSTEM task to export registry keys..." -ForegroundColor Cyan
Register-ScheduledTask -TaskName $taskName -Action $action -Principal $principal -Settings $settings -Force | Out-Null

try {
    # 3. Execute and Wait for Scheduled Task
    Write-Host "[*] Running export task..." -ForegroundColor Cyan
    Start-ScheduledTask -TaskName $taskName
    
    $timeoutSeconds = 10
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
        throw "Registry export task timed out or failed to write output."
    }
    
} finally {
    # 4. Clean up Scheduled Task
    Write-Host "[*] Cleaning up temporary export task..." -ForegroundColor Cyan
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue | Out-Null
}

# 5. Parse registry export file
Write-Host "[*] Parsing registry data..." -ForegroundColor Cyan
$rawLines = Get-Content $tempRegFile -Encoding Unicode

# Preprocess to join registry line continuations (lines ending with \)
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

# Delete the temporary REG file immediately after reading
if (Test-Path $tempRegFile) { Remove-Item $tempRegFile -Force }

$adapters = @{}
$currentAdapter = $null
$currentDeviceMac = $null
$currentDeviceData = $null

foreach ($line in $lines) {
    if ([string]::IsNullOrWhiteSpace($line) -or $line.StartsWith(";")) { continue }

    if ($line.StartsWith("[") -and $line.EndsWith("]")) {
        $keyPath = $line.Substring(1, $line.Length - 2)
        
        # Match HKLM\...\Keys\<AdapterMAC> or HKLM\...\Keys\<AdapterMAC>\<DeviceMAC>
        if ($keyPath -match "BTHPORT\\Parameters\\Keys\\(?<subPath>[^\\]+(\\[^\\]+)?)$") {
            $subPath = $Matches['subPath']
            $parts = $subPath.Split('\')
            
            if ($parts.Length -eq 1) {
                # Adapter Key
                $adapterMacRaw = $parts[0].ToUpper()
                $adapterMacFormatted = ($adapterMacRaw -replace '..(?!$)', '$0:').ToUpper()
                $currentAdapter = $adapterMacRaw
                $currentDeviceMac = $null
                $currentDeviceData = $null
                
                if (-not $adapters.ContainsKey($currentAdapter)) {
                    $adapters[$currentAdapter] = [ordered]@{
                        adapter = $adapterMacFormatted
                        devices = @()
                    }
                }
            } elseif ($parts.Length -eq 2) {
                # BLE Device Subkey (inside Adapter)
                $adapterMacRaw = $parts[0].ToUpper()
                $deviceMacRaw = $parts[1].ToUpper()
                $deviceMacFormatted = ($deviceMacRaw -replace '..(?!$)', '$0:').ToUpper()
                
                $currentAdapter = $adapterMacRaw
                $currentDeviceMac = $deviceMacRaw
                
                if (-not $adapters.ContainsKey($currentAdapter)) {
                    $adapters[$currentAdapter] = [ordered]@{
                        adapter = ($adapterMacRaw -replace '..(?!$)', '$0:').ToUpper()
                        devices = @()
                    }
                }
                
                $deviceName = Get-DeviceFriendlyName $deviceMacRaw
                $currentDeviceData = [ordered]@{
                    mac  = $deviceMacFormatted
                    name = $deviceName
                    type = "LE"
                }
                $adapters[$currentAdapter].devices += $currentDeviceData
            }
        } else {
            $currentAdapter = $null
            $currentDeviceMac = $null
            $currentDeviceData = $null
        }
    } elseif ($line -match '^"([^"]+)"\s*=\s*(.+)$') {
        $valName = $Matches[1]
        $valVal = $Matches[2]
        
        if ($currentAdapter -and $null -eq $currentDeviceMac) {
            # Classic Device Link Key under Adapter Key (Value name is Device MAC)
            if ($valName -match "^[0-9a-fA-F]{12}$") {
                $deviceMacRaw = $valName.ToUpper()
                $deviceMacFormatted = ($deviceMacRaw -replace '..(?!$)', '$0:').ToUpper()
                
                $keyHex = ""
                if ($valVal.StartsWith("hex:")) {
                    $keyHex = $valVal.Substring(4).Replace(",", "").Replace(" ", "").ToUpper()
                }
                
                $deviceName = Get-DeviceFriendlyName $deviceMacRaw
                $deviceObj = [ordered]@{
                    mac  = $deviceMacFormatted
                    name = $deviceName
                    type = "Classic"
                    key  = $keyHex
                }
                $adapters[$currentAdapter].devices += $deviceObj
            }
        } elseif ($currentDeviceMac -and $currentDeviceData) {
            # BLE Device Key details
            if ($valName -eq "LTK") {
                if ($valVal.StartsWith("hex:")) {
                    $currentDeviceData.ltk = $valVal.Substring(4).Replace(",", "").Replace(" ", "").ToUpper()
                }
            } elseif ($valName -eq "ERand") {
                if ($valVal.StartsWith("hex:")) {
                    $eRandHex = $valVal.Substring(4).Replace(",", "").Replace(" ", "").ToUpper()
                    $currentDeviceData.rand = Convert-ERandToRand $eRandHex
                }
            } elseif ($valName -eq "EDIV") {
                if ($valVal.StartsWith("dword:")) {
                    $currentDeviceData.ediv = [Convert]::ToInt32($valVal.Substring(6), 16)
                }
            } elseif ($valName -eq "IRK") {
                if ($valVal.StartsWith("hex:")) {
                    $currentDeviceData.irk = $valVal.Substring(4).Replace(",", "").Replace(" ", "").ToUpper()
                }
            } elseif ($valName -eq "CSRK") {
                if ($valVal.StartsWith("hex:")) {
                    $currentDeviceData.csrk = $valVal.Substring(4).Replace(",", "").Replace(" ", "").ToUpper()
                }
            }
        }
    }
}

# 6. Format and Output JSON
$adaptersList = @()
foreach ($key in $adapters.Keys) {
    if ($adapters[$key].devices.Count -gt 0) {
        $adaptersList += $adapters[$key]
    }
}

if ($adaptersList.Count -eq 0) {
    Write-Host "[WARNING] No Bluetooth adapters or devices found with pairing keys." -ForegroundColor Yellow
    Exit 0
}

# Write output JSON to btkeys.json in current directory
$jsonContent = ConvertTo-Json -InputObject $adaptersList -Depth 100
$outputPath = Join-Path (Get-Location) "btkeys.json"
Set-Content -Path $outputPath -Value $jsonContent -Encoding UTF8

# 7. Print Console Summary
Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "          EXPORT COMPLETED SUCCESSFULLY  " -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host "Saved JSON export to: $outputPath" -ForegroundColor Cyan
Write-Host ""

foreach ($adapterObj in $adaptersList) {
    Write-Host "Adapter" -ForegroundColor White -FontWeight Bold
    Write-Host "  $($adapterObj.adapter)" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "Devices" -ForegroundColor White -FontWeight Bold
    
    foreach ($device in $adapterObj.devices) {
        Write-Host "  $($device.name)" -ForegroundColor Yellow
        Write-Host "    MAC   : $($device.mac)" -ForegroundColor DarkGray
        Write-Host "    Type  : $($device.type)" -ForegroundColor DarkGray
        
        if ($device.type -eq "Classic") {
            Write-Host "    KEY   : $($device.key)" -ForegroundColor Cyan
        } else {
            if ($device.ltk)  { Write-Host "    LTK   : $($device.ltk)" -ForegroundColor Cyan }
            if ($device.ediv) { Write-Host "    EDIV  : $($device.ediv)" -ForegroundColor DarkCyan }
            if ($device.rand) { Write-Host "    RAND  : $($device.rand)" -ForegroundColor DarkCyan }
        }
        Write-Host ""
    }
}
