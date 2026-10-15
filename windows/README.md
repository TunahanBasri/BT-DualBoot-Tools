# Windows Key Export Guide 🪟

This component exports Bluetooth Link Keys from the Windows registry to an interoperable JSON format (`btkeys.json`).

---

## 🔒 Security & Privilege Architecture

In Windows 10/11, Bluetooth link keys are stored under:
```text
HKLM\SYSTEM\CurrentControlSet\Services\BTHPORT\Parameters\Keys
```

This registry hive has an Access Control List (ACL) that restricts read access exclusively to **`NT AUTHORITY\SYSTEM`**. Even an elevated Administrator cannot read this key directly via standard registry queries.

### How `Export-BluetoothKeys.ps1` Works Safely:
1. **Verification**: Checks if the PowerShell session has Administrator privileges.
2. **Ephemeral Task**: Registers a temporary Windows Scheduled Task set to run as `NT AUTHORITY\SYSTEM`.
3. **Execution**: The task invokes `reg export` to write the keys to a temporary file in `$env:TEMP`.
4. **Cleanup Guarantee**: Inside a `try ... finally` block, the scheduled task is **immediately unregistered**, and the temporary file is deleted from disk right after being parsed into memory.
5. **JSON Generation**: Outputs `btkeys.json` with resolved friendly device names (e.g., Logitech MX Master 3, Keychron K2).

---

## 🚀 How to Run

1. Open **PowerShell as Administrator** (Right-click -> *Run as administrator*).
2. Navigate to this directory and execute:
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force
   .\Export-BluetoothKeys.ps1
   ```
3. A file named `btkeys.json` will be generated in your current directory.
4. Copy `btkeys.json` to an accessible location on your Linux partition (or a shared FAT32/NTFS drive).
