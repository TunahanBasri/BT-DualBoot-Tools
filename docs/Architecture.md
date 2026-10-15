# System Architecture & Flow Design 🏛️

**BT-DualBoot Tools** solves the chronic dual-boot Bluetooth de-synchronization problem by bridging the architectural divide between the **Windows NT Kernel (BTHPORT)** and the **Linux BlueZ Bluetooth Subsystem**.

---

## 1. High-Level Synchronization Pipeline

```mermaid
flowchart TD
    subgraph Windows [" Windows Subsystem "]
        A[Administrator Session] -->|Triggers| B[Export-BluetoothKeys.ps1]
        B -->|Ephemeral Task| C[NT AUTHORITY/SYSTEM]
        C -->|reg export| D[BTHPORT/Parameters/Keys]
        D -->|In-Memory Parse| E[Friendly Name Resolution]
        E -->|Atomic Write| F[btkeys.json]
    end

    subgraph Transfer [" Partition / Flash / Shared Drive "]
        F --> G[(btkeys.json)]
    end

    subgraph Linux [" Linux Subsystem (BlueZ) "]
        G -->|Imports| H[bt-dualboot CLI]
        H -->|Validation| I[parse_export_json]
        H -->|Safety First| J[create_backup]
        J -->|Timestamped Snapshot| K[/var/lib/bluetooth_backup_*]
        I -->|Inspection Plan| L{--dry-run ?}
        L -->|Yes| M[Display Diff Table & Exit]
        L -->|No| N[Apply LinkKey into info INI]
        N -->|systemctl restart| O[bluetoothd Daemon]
        O --> P[Seamless Connection Established 🎉]
    end
```

---

## 2. Component Breakdown

### A. Windows Key Extractor (`windows/Export-BluetoothKeys.ps1`)
- **Access Control Isolation**: Because `BTHPORT\Parameters\Keys` is restricted to `NT AUTHORITY\SYSTEM`, the script provisions an ephemeral scheduled task (`BTDualBoot_ExportKeys_<GUID>`).
- **Zero-Residual Principle**: Using a strict `try ... finally` block, the scheduled task is unregistered and the temporary `.reg` export is wiped immediately upon memory parsing.
- **Friendly Name Resolver**: Queries `BTHPORT\Parameters\Devices\<MAC>` and the PnP subsystem to resolve human-readable device names (e.g., *Logitech MX Master 3*).

### B. Core Python Engine (`src/bt_dualboot/core/`)
- **`crypto.py`**: Validates MAC addresses and 128-bit LinkKeys; houses endianness conversion logic for the BLE roadmap.
- **`registry.py`**: Parses and validates the schema of incoming JSON files, enforcing type safety and sanitized hex strings.
- **`bluez.py`**: A non-destructive INI parser that locates device directories under `/var/lib/bluetooth/` and updates `[LinkKey]` while preserving all existing custom properties and comments.

### C. Safety & Snapshot Manager (`src/bt_dualboot/utils/backup.py`)
- Automatically captures a timestamped copy of `/var/lib/bluetooth` before applying updates.
- Offers instant restoration via `bt-dualboot --rollback [latest|path]`.

---

## 3. Data Schema (`btkeys.json`)

The exported data adheres to a strict, validated schema:

```json
[
  {
    "adapter": "4C:03:4F:E0:D1:B0",
    "devices": [
      {
        "mac": "54:46:6B:00:09:FB",
        "name": "Logitech MX Master 3",
        "key": "588546EA82C033CE9508E1C74EC74FD6"
      }
    ]
  }
]
```
