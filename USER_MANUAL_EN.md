# STANDARD OPERATING PROCEDURE (SOP)
## BLUETOOTH PAIRING KEY SYNCHRONIZATION FOR DUAL-BOOT COMPUTERS

> A concise, step-by-step technical operating guide for dual-boot systems.

---

## 1. SCOPE AND PURPOSE

This document gives the standard operating procedure to synchronize Bluetooth peripheral keys between Microsoft Windows and Linux BlueZ on dual-boot computers. 

This procedure prevents the loss of connection when you change operating systems.

---

## 2. TOOLS AND PREREQUISITES

### A. Hardware Required
1. Dual-boot personal computer with Microsoft Windows and Linux installed on separate partitions or disks.
2. Bluetooth Host Controller (internal or external USB adapter).
3. Bluetooth peripheral device (keyboard, mouse, or audio device).
4. File transfer medium (WhatsApp Web, Cloud Storage, direct Windows partition access, or a USB flash drive).

### B. Software and Permissions Required
1. Microsoft Windows 10 or Windows 11 (Administrator privilege required).
2. Linux distribution with BlueZ 5.x stack (Root or `sudo` privilege required).
3. Python 3.8 or higher installed on Linux.

---

## 3. TECHNICAL BACKGROUND

> [!NOTE]
> A Bluetooth peripheral device stores only one link key in its non-volatile memory. When you pair the peripheral with Windows, Windows writes a new key to the device. The older Linux key becomes invalid.
> This procedure copies the latest Windows link key to the Linux configuration directory.

---

## 4. STANDARD OPERATING PROCEDURE (SOP)

```text
+-------------------+      +---------------------+      +---------------------+
|      TASK 01      |      |       TASK 02       |      |       TASK 03       |
| Pair on Linux     | ---> | Pair on Windows     | ---> | Run Export-Keys.bat |
| (Creates Profile) |      | (Generates New Key) |      | (Outputs JSON)      |
+-------------------+      +---------------------+      +---------------------+
                                                                   |
                                                                   v
+-------------------+      +---------------------+      +---------------------+
|    ALL SYSTEMS    |      |       TASK 05       |      |       TASK 04       |
| Direct Connection | <--- | Run sync.py on      | <--- | Transfer btkeys.json|
| Verified (Done!)  |      | Linux (Syncs BlueZ) |      | (WhatsApp/Cloud/USB)|
+-------------------+      +---------------------+      +---------------------+
```

### SUBTASK 01: PAIR THE PERIPHERAL DEVICE IN LINUX
1. Start the computer in Linux.
2. Open the system Bluetooth settings menu.
3. Set your Bluetooth keyboard or mouse to pairing mode.
4. Connect the device through the Linux user interface.
5. Make sure the device operates correctly.
6. Do not remove the pairing.

> [!CAUTION]
> You must complete SUBTASK 01 first. Linux creates the internal device hardware profile and GATT configuration during this step. If you omit this step, the synchronization will fail.

---

### SUBTASK 02: PAIR THE PERIPHERAL DEVICE IN WINDOWS
1. Restart the computer.
2. Start the computer in Microsoft Windows.
3. Open **Settings > Bluetooth & devices**.
4. Set your Bluetooth keyboard or mouse to pairing mode again.
5. Connect the device through the Windows user interface.
6. Make sure the device operates correctly.

---

### SUBTASK 03: EXTRACT REGISTRY KEYS IN WINDOWS
1. Open the `bt-dualboot-tools` project folder in Windows.
2. Right-click the file `Export-Keys.bat`.
3. Select **Run as administrator**.
4. Wait for the script to finish.
5. Verify that the terminal shows the message:
   `KEY TEBRIKLER! BLUETOOTH ANAHTAR PAKETINIZ HAZIR (btkeys.json)`
6. Verify that the file `btkeys.json` is created in the folder.

---

### SUBTASK 04: TRANSFER THE KEY PACKAGE TO LINUX
Transfer `btkeys.json` to your Linux environment using any of the following methods:
- **Method A (Cloud / Messaging):** Send `btkeys.json` to yourself via WhatsApp Web, Telegram, Google Drive, or Email, then download it in Linux.
- **Method B (Direct Partition Access):** In Linux, access your Windows `C:\` partition directly via the file manager.
- **Method C (USB Storage Device):** Copy `btkeys.json` onto an external USB flash drive.

> [!NOTE]
> 🔒 **Security Best Practice:** Bluetooth Link Keys are cryptographic secrets. If you transfer `btkeys.json` via messaging or cloud (WhatsApp/Telegram/Email), delete the file/message from your chat and downloads once synchronization is complete.

---

### SUBTASK 05: SYNCHRONIZE KEYS IN LINUX
1. Restart the computer in Linux.
2. Open a terminal window in the `bt-dualboot-tools` project folder.
3. Execute the following command:
   ```bash
   sudo python sync.py
   ```
4. Drag and drop the `btkeys.json` file (from Downloads, USB, or C:\) into the terminal window.
5. Press the `Enter` key.
6. The system executes the following automatic actions:
   - Creates a timestamped backup in `/var/lib/bluetooth/backups/`.
   - Injects and configures pairing keys in `/var/lib/bluetooth/[Adapter]/[Device]/info`.
   - Restarts the `bluetooth` service.

---

## 5. POST-SYNCHRONIZATION VERIFICATION

1. Verify the live status output displayed on the terminal:
   ```text
   Canlı Bağlantı Durumu:
    ✔ [Device Name] -> ANINDA BAĞLANDI!
   ```
2. Move your Bluetooth mouse or type on your Bluetooth keyboard.
3. Make sure the input response is instantaneous.
4. Restart the computer in Windows. Make sure the device connects without re-pairing.
5. Restart the computer in Linux. Make sure the device connects without re-pairing.

---

## 6. CONTINGENCY AND ROLLBACK PROCEDURE

If a connection failure occurs:

1. Open the terminal in Linux.
2. Run the rollback command:
   ```bash
   sudo python sync.py --rollback latest
   ```
3. The system restores the previous configuration snapshot.
4. Restart the Bluetooth service:
   ```bash
   sudo systemctl restart bluetooth
   ```
