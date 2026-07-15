# Linux BlueZ Directory and Config Structure

This document outlines the file layout and configuration format used by **BlueZ** (the official Linux Bluetooth protocol stack) to store pairing info, and explains how this tool integrates keys into it.

## File Paths

On Linux, BlueZ configurations are managed by the `bluetoothd` daemon and stored inside:
`/var/lib/bluetooth/`

This directory has restricted permissions (usually `drwx------` owned by `root`), preventing standard users from listing or modifying its contents.

Inside `/var/lib/bluetooth/`, the folder structure is organized by Bluetooth Adapter and Device MAC addresses:
```
/var/lib/bluetooth/
└── {Adapter-MAC}/
    ├── settings            # Adapter settings
    └── {Device-MAC}/
        └── info            # Device connection parameters & pairing keys
```

*   **Format**: The MAC addresses are formatted in **lowercase** and delimited by **colons** (e.g. `/var/lib/bluetooth/4c:03:4f:e0:d1:b0/54:46:6b:00:09:fb/info`).

---

## The `info` Configuration File

The `info` file is structured like a standard INI file (key-value properties grouped into sections). The Bluetooth daemon reads this file on startup and caches the keys in memory.

### 1. Classic Bluetooth Keys (`[LinkKey]`) - Supported in v1.0
For Classic Bluetooth devices, the credentials are stored under the `[LinkKey]` section:

```ini
[LinkKey]
Key=588546EA82C033CE9508E1C74EC74FD6
Type=0
PINLength=0
```
*   **Key**: The 128-bit pairing key. It must be a **32-character uppercase hex string** without spaces or colons.
*   **Type**: Integer representing the key type (e.g. `0` for Combination Key, `4` for Debug Key). Defaulted to `0` by this script if not already present.
*   **PINLength**: PIN length used during pairing (usually `0`).

---

### 2. Bluetooth Low Energy Keys (Roadmap v1.1)

LE devices require several keys and parameters to establish encrypted sessions.

#### A. Long Term Key (`[LongTermKey]`)
Stores the encryption key along with validation credentials distributed during initial bonding:

```ini
[LongTermKey]
Key=C2329712FF75225E0A6F4E8588546E8B
Authenticated=0
EncSize=16
EDiv=48215
Rand=165487452654789520
```

#### B. Identity Resolving Key (`[IdentityResolvingKey]`)
```ini
[IdentityResolvingKey]
Key=D182A54BE499F5E68AB828B1089EE239
```

#### C. Local Signature Key (`[LocalSignatureKey]`)
```ini
[LocalSignatureKey]
Key=F5282B4310E6FBC95D3E21FA889DE203
```

---

## Integration Workflow

The Linux import script (`import_key.py`) operates as follows:

1.  **Backup**: Triggers `backup.py` to recursively copy `/var/lib/bluetooth` to `/var/lib/bluetooth_backup_<timestamp>`.
2.  **Target Verification**: Searches case-insensitively for the matching `{Adapter-MAC}` and `{Device-MAC}` folders under `/var/lib/bluetooth`.
3.  **Config Parsing & Replacing**:
    *   Opens the device's `info` file.
    *   Walks the lines to find target keys within the `[LinkKey]` section.
    *   Overwrites existing keys with values from the exported `btkeys.json`.
    *   If the section is missing, it appends it with standard parameters.
    *   Strictly preserves all other keys, spacing, and comments.
4.  **Daemon Reload**: Reloads the changes by restarting the BlueZ systemd service:
    `systemctl restart bluetooth`
