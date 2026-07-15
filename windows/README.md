# BT DualBoot Tools - Windows Export (v1.0)

This folder contains the script to export Classic Bluetooth pairing keys from the Windows registry.

## Contents
*   `Export-BluetoothKeys.ps1`: The core PowerShell script that performs the registry export, parsing, and JSON generation.

## How it Works
The Windows registry stores Bluetooth pairing keys under `HKLM\SYSTEM\CurrentControlSet\Services\BTHPORT\Parameters\Keys`. By default, only the `SYSTEM` account has permission to read these keys.

To circumvent this without third-party utilities (like `PsExec`), the PowerShell script:
1.  Creates a temporary Scheduled Task running under the `NT AUTHORITY\SYSTEM` account.
2.  Runs `reg export` to write the keys to a temporary UTF-16LE registry file in the user's temp directory.
3.  Starts the task and waits for it to complete.
4.  Deletes the task and parses the generated registry file.
5.  Extracts adapter MACs and Classic keys (`LinkKey`) for paired devices.
6.  Resolves the device names from `HKLM\SYSTEM\CurrentControlSet\Services\BTHPORT\Parameters\Devices` (which is readable by local Administrators).
7.  Saves the data in the current folder as `btkeys.json` and outputs a summary to the console.

*Note: Bluetooth Low Energy (LE) device extraction is not supported in v1.0 and is planned for v1.1.*

## Prerequisites
*   Windows 10 / 11.
*   PowerShell 5.1 or newer.
*   Administrator privileges.

## Usage

Open an **Administrator PowerShell** terminal, navigate to this folder, and run:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
.\Export-BluetoothKeys.ps1
```

---

## Output Format (`btkeys.json`)
The script generates a file named `btkeys.json` in your current working directory. The structure lists devices by adapter:

```json
[
  {
    "adapter": "4C:03:4F:E0:D1:B0",
    "devices": [
      {
        "mac": "54:46:6B:00:09:FB",
        "name": "Piranha-2375",
        "key": "588546EA82C033CE9508E1C74EC74FD6"
      }
    ]
  }
]
```
