# Linux BlueZ Directory and Config Structure 🐧

This document outlines the filesystem hierarchy and INI structure utilized by **BlueZ** (the official Linux Bluetooth protocol stack) to store pairing state.

---

## 1. Storage Location & Security

On modern Linux distributions (Ubuntu, Debian, Fedora, Arch Linux, openSUSE), Bluetooth device configurations are maintained by `bluetoothd` under:

```text
/var/lib/bluetooth/
```

- **Permissions**: `drwx------` (mode 0700), owned by `root:root`.
- **Directory Hierarchy**:
  ```text
  /var/lib/bluetooth/
  └── <Adapter-MAC>/              # e.g., 4c:03:4f:e0:d1:b0
      ├── settings                # Local adapter parameters
      └── <Device-MAC>/           # e.g., 54:46:6b:00:09:fb
          └── info                # INI configuration & pairing keys
  ```

---

## 2. The `info` Configuration File

The `info` file is formatted as a standard INI configuration.

```ini
[General]
Name=Logitech MX Master 3
Class=0x000580
SupportedTechnologies=BR/EDR;
Trusted=true
Blocked=false

[LinkKey]
Key=588546EA82C033CE9508E1C74EC74FD6
Type=0
PINLength=0
```

### Critical Rules for Manipulating `info`:
1. **Never Overwrite Blindly**: Replacing the whole file destroys vital adapter pairing parameters (such as `Class`, `SupportedTechnologies`, `Services`, and `Trusted` flags).
2. **Preserve Comments & Whitespace**: Standard INI writers like Python's built-in `configparser` strip comments and rearrange sections alphabetically, which can cause subtle parsing quirks in older `bluetoothd` versions.
3. **Daemon Reload**: `bluetoothd` caches pairing keys in memory upon initialization. Modifying `info` on disk requires restarting the daemon (`systemctl restart bluetooth`) or triggering a BlueZ DBus reload for changes to take effect.
