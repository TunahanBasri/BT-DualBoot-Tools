# Explanation: Linux BlueZ Storage & Non-Destructive INI Parsing 🐧

This document explains how Linux BlueZ stores Bluetooth device pairing configurations and why standard Python `configparser` is unsuitable for modifying them.

---

## 1. BlueZ Directory Structure

BlueZ maintains pairing states in `/var/lib/bluetooth`:

```text
/var/lib/bluetooth/
└── 4C:03:4F:E0:D1:B0/                 # Host Adapter MAC
    ├── settings                       # Adapter global settings
    └── 54:46:6B:00:09:FB/             # Paired Device MAC
        └── info                       # Pairing properties (INI format)
```

---

## 2. Structure of an `info` File

The `info` file is structured like an INI file:

```ini
[General]
Name=Logitech MX Master 3
Appearance=0x03c2
AddressType=public
SupportedTechnologies=BR/EDR;
Trusted=true
Blocked=false
Services=00001124-0000-1000-8000-00805f9b34fb;

[LinkKey]
Key=588546EA82C033CE9508E1C74EC74FD6
Type=4
PINLength=0

[DeviceID]
Source=2
Vendor=1133
Product=45091
Version=2
```

---

## 3. Why `configparser` Fails for BlueZ

Standard Python `configparser.ConfigParser()` exhibits several behaviors that can corrupt or destabilize BlueZ:
1. **Case-Insensitivity**: By default, it lowercases section and property keys (`key` instead of `Key`), which `bluetoothd` may ignore.
2. **Comment Stripping**: It discards all comments and blank lines.
3. **Key Reordering**: It does not guarantee preserving the original order of sections or properties.
4. **Delimiter Alteration**: It rewrites spaces around delimiters (`Key = ...` instead of `Key=...`).

### The Solution: Non-Destructive Parsing
`bt_dualboot.core.bluez` uses a lightweight non-destructive stream parser:
- It processes the file line-by-line.
- It leaves all unrelated sections, blank lines, and comments completely untouched.
- It targets solely the `[LinkKey]` section, updating the `Key=` property in-place or appending the section cleanly if absent.
- It writes atomically to disk using `.info.tmp.<pid>` and `os.replace` to prevent filesystem corruption.
