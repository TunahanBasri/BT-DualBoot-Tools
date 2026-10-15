# 🚀 Quickstart: Seamless Dual-Boot Bluetooth Sync in 5 Minutes

Welcome to **BT-DualBoot Tools**! This guide walks you through pairing your Bluetooth devices (mouse, keyboard, headphones) so they work across both **Windows** and **Linux** without ever requiring re-pairing when you reboot.

---

## 📋 Prerequisites

1. A computer with dual-boot (Windows 10/11 and Linux with BlueZ 5.x).
2. Administrator privileges on Windows.
3. Sudo / root privileges on Linux.
4. Python 3.8 or higher installed on either system.

---

## ⏱️ Step-by-Step Walkthrough

```
[ Step 1: Linux ]               [ Step 2: Windows ]               [ Step 3: Linux ]
 Pair Peripherals    ──reboot──> Pair Peripherals & Export ──reboot──> Sync Keys Instantly
 (Generates folder)             (Generates btkeys.json)           (bt-dualboot CLI)
```

### Step 1: Pair Once in Linux
1. Boot into **Linux**.
2. Open Bluetooth Settings and pair your Bluetooth peripherals (e.g. Logitech MX Master 3, Keychron K2) normally.
3. *Why?* This creates the device directory structure under `/var/lib/bluetooth/<AdapterMAC>/<DeviceMAC>/`.

### Step 2: Pair in Windows and Export Keys
1. Reboot into **Windows**.
2. Open Bluetooth Settings and pair the **exact same** peripherals.
3. Open **PowerShell as Administrator** and navigate to this repository:
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force
   .\windows\Export-BluetoothKeys.ps1
   ```
4. A file named `btkeys.json` will be generated in your folder. Copy this file to a shared NTFS drive, FAT32 partition, or USB flash drive.

### Step 3: Sync Pairing Keys in Linux
1. Reboot back into **Linux**.
2. Preview the synchronization with simulation mode:
   ```bash
   python -m bt_dualboot.cli /path/to/btkeys.json --dry-run
   ```
3. Apply the changes with root privileges:
   ```bash
   sudo python -m bt_dualboot.cli /path/to/btkeys.json
   ```
   *(Or if installed via `pip install .`: `sudo bt-dualboot /path/to/btkeys.json`)*
4. **Done!** The tool creates an automated snapshot backup, injects the Windows LinkKey into BlueZ, and reloads `bluetoothd`. Your mouse and keyboard will connect immediately!

---

## ❓ What's Next?
- [Detailed Device Sync Guide](../how-to/sync-devices.md)
- [How to Restore / Rollback](../how-to/rollback-backup.md)
- [Understanding Bluetooth Cryptography](../explanation/bluetooth-cryptography.md)
