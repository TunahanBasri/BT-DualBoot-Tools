# Windows Bluetooth Registry Structure

This document details where and how Windows stores Bluetooth pairing keys, and explains the security restrictions and extraction methods used by this tool.

## Registry Paths

Windows stores Bluetooth configurations under the registry path:
`HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\BTHPORT\Parameters`

Under this path, two subkeys are critical for synchronization:
1.  `Devices/` (Readable by Administrators)
2.  `Keys/` (Restricted to `SYSTEM` account)

---

## 1. Device Friendly Names (`Devices/`)

Each paired Bluetooth device has a subkey under `Devices/` named by its MAC address in lowercase hexadecimal format (e.g. `54466b0009fb`).

An administrator can read this key. Inside, the value `Name` is of type `REG_BINARY` and contains the device friendly name as a null-terminated UTF-8 byte array.
*   **Example Value**: `Name = 50 69 72 61 6e 68 61 2d 32 33 37 35 00` (hex representation of `Piranha-2375\0`)

This tool decodes the `Name` byte array to present human-readable names alongside MAC addresses.

---

## 2. Pairing Keys (`Keys/`)

Pairing keys are stored under `Keys/{Adapter-MAC}` where `{Adapter-MAC}` is the MAC address of the host Bluetooth adapter (e.g. `4c034fe0d1b0`).

### Security Restrictions
By default, the `Keys/` subkey has security ACLs that prevent even the local `Administrators` group or the `Administrator` user from reading it. The key is owned by and accessible only to the **`NT AUTHORITY\SYSTEM`** (Local System) account.

To view or export these keys, a process must run with SYSTEM privileges.

### Classic Bluetooth Keys (Supported in v1.0)
For Classic Bluetooth devices, the link keys are stored as registry values under the Adapter subkey.
*   **Value Name**: The Device MAC (12 lowercase hex characters, e.g. `54466b0009fb`).
*   **Type**: `REG_BINARY`
*   **Size**: 16 bytes (128-bit Link Key).
*   **Example**: `"54466b0009fb"=hex:58,85,46,ea,82,c0,33,ce,95,08,e1,c7,4e,c7,4f,d6`

### Bluetooth Low Energy (LE) Keys (Roadmap v1.1)
For Low Energy (LE) devices, Windows creates a nested registry subkey under the Adapter key named after the Device MAC.
*   **Subkey Path**: `BTHPORT\Parameters\Keys\{Adapter-MAC}\{Device-MAC}`
*   **Values**:
    *   `LTK` (Long Term Key): `REG_BINARY` (16 bytes) - used for link encryption.
    *   `KeyLength`: `REG_DWORD` - size of the key, usually `0x10` (16 bytes).
    *   `ERand` (Randomizer): `REG_BINARY` (8 bytes) - random number sent by the peripheral.
    *   `EDIV` (Encrypted Diversifier): `REG_DWORD` - diversifier sent by the peripheral.
    *   `IRK` (Identity Resolving Key): `REG_BINARY` (16 bytes).
    *   `CSRK` (Connection Signature Resolving Key): `REG_BINARY` (16 bytes).

---

## Extraction Method

To export the keys without requiring external compiled binaries (like Sysinternals `PsExec`), `Export-BluetoothKeys.ps1` executes the following sequence:

1.  **Privilege Check**: Checks if the PowerShell session is elevated (run as Administrator).
2.  **Task Creation**: Registers a temporary Windows Scheduled Task named `ExportBluetoothKeysTemp`.
    *   The task action is set to execute: `reg export HKLM\SYSTEM\CurrentControlSet\Services\BTHPORT\Parameters\Keys "$env:TEMP\btkeys_temp.reg" /y`
    *   The task principal is set to run under the **`NT AUTHORITY\SYSTEM`** account.
3.  **Task Execution**: Starts the task and loops until the state changes to `Ready` or `Disabled` (indicating completion).
4.  **Parsing & Cleanup**:
    *   Reads the output file (`btkeys_temp.reg`) encoded in UTF-16LE.
    *   Deletes the scheduled task immediately.
    *   Deletes the temporary `.reg` file as soon as the in-memory parse begins.
