# Windows Bluetooth Subsystem & Registry Internals 🪟

This technical document details how the Windows NT Kernel stores Bluetooth link keys, the security barriers protecting them, and how `Export-BluetoothKeys.ps1` reliably extracts them.

---

## 1. Registry Architecture (`BTHPORT`)

Bluetooth keys and device configurations are managed by the kernel Bluetooth port driver (`bthport.sys`) and persisted in the Windows Registry under:

```text
HKLM\SYSTEM\CurrentControlSet\Services\BTHPORT\Parameters
```

Inside this path, two critical subkeys exist:

### A. Device Friendly Names (`Parameters\Devices\<DeviceMAC>`)
- **Access Level**: Readable by standard Administrators.
- **Key Name**: 12 lowercase hexadecimal digits representing the device MAC address (e.g., `54466b0009fb`).
- **Value**: `Name` (`REG_BINARY`). Null-terminated UTF-8 byte array containing the advertised friendly name (e.g., `"Logitech MX Master 3\0"`).

### B. Device Pairing Keys (`Parameters\Keys\<AdapterMAC>`)
- **Access Level**: **STRICTLY RESTRICTED TO `NT AUTHORITY\SYSTEM`**.
- Even a local Administrator attempting `reg query` on this key will receive `ERROR: ACCESS IS DENIED`.
- For Classic Bluetooth: Each paired device has a binary value whose name is the device MAC and whose data is the 16-byte Link Key.

---

## 2. SYSTEM Privilege Escalation Strategy

Many community scripts require users to install third-party closed-source binaries (e.g., Sysinternals `PsExec.exe`) or download untrusted C utilities to obtain SYSTEM privileges.

**BT-DualBoot Tools relies 100% on native Windows components**:
1. **Scheduled Task Provider**: Windows allows an elevated Administrator to register a Scheduled Task that executes under the `NT AUTHORITY\SYSTEM` service account.
2. **Ephemeral Action**: The task executes `cmd.exe /c reg export HKLM\...\Keys "<temp_file>" /y`.
3. **Execution & Wait**: PowerShell starts the task and polls until completion (typically under 1.5 seconds).
4. **Immediate Cleanup**:
   - The task is immediately deleted (`Unregister-ScheduledTask`).
   - The temporary `.reg` export is parsed in memory and unlinked from the filesystem.
   - Guaranteed cleanup is ensured via PowerShell's `finally` block.
