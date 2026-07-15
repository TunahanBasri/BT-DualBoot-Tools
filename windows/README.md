# BT DualBoot Tools - Windows Export

This folder contains scripts to export Bluetooth pairing keys (both Classic and Low Energy) from the Windows registry.

## Contents
*   `Export-BluetoothKeys.ps1`: The core PowerShell script that performs the registry export, parsing, and JSON generation.
*   `Export-BluetoothKeys.py`: A Python wrapper script that automatically requests Administrator permissions and runs the PowerShell script.

## How it Works
The Windows registry stores Bluetooth pairing keys under `HKLM\SYSTEM\CurrentControlSet\Services\BTHPORT\Parameters\Keys`. By default, only the `SYSTEM` account has permission to read these keys.

To circumvent this without third-party utilities (like `PsExec`), the PowerShell script:
1.  Creates a temporary Scheduled Task running under the `NT AUTHORITY\SYSTEM` account.
2.  Runs `reg export` to write the keys to a temporary UTF-16LE registry file in the user's temp directory.
3.  Starts the task and waits for it to complete.
4.  Deletes the task and parses the generated registry file.
5.  Extracts adapter MACs, Classic keys (`LinkKey`), and Bluetooth Low Energy keys (`LTK`, `EDiv`, `Rand`, `IRK`, `CSRK`).
6.  Resolves the device names from `HKLM\SYSTEM\CurrentControlSet\Services\BTHPORT\Parameters\Devices` (which is readable by local Administrators).
7.  Saves the data in the current folder as `btkeys.json` and outputs a summary to the console.

## Prerequisites
*   Windows 10 / 11.
*   PowerShell 5.1 or newer.
*   Administrator privileges.

## Usage

### Method 1: Using the PowerShell Script (Recommended)
Open an **Administrator PowerShell** terminal, navigate to this folder, and run:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
.\Export-BluetoothKeys.ps1
```

### Method 2: Using the Python Script
Open a command prompt or terminal and run:

```cmd
python Export-BluetoothKeys.py
```
*(This will automatically trigger a User Account Control (UAC) prompt to elevate to Administrator before running.)*

---

## Output Format (`btkeys.json`)
The script generates a file named `btkeys.json` in your current working directory. The structure accommodates multiple adapters and lists devices categorized by Classic vs LE:

```json
[
  {
    "adapter": "4C:03:4F:E0:D1:B0",
    "devices": [
      {
        "mac": "54:46:6B:00:09:FB",
        "name": "Piranha-2375",
        "type": "Classic",
        "key": "588546EA82C033CE9508E1C74EC74FD6"
      },
      {
        "mac": "00:11:22:33:44:55",
        "name": "Bluetooth LE Mouse",
        "type": "LE",
        "ltk": "C2329712FF75225E0A6F4E8588546E8B",
        "ediv": 48215,
        "rand": "165487452654789520",
        "irk": "D182A54BE499F5E68AB828B1089EE239",
        "csrk": "F5282B4310E6FBC95D3E21FA889DE203"
      }
    ]
  }
]
```
