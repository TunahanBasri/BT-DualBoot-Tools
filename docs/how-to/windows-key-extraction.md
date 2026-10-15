# How-To: Extract Bluetooth Keys in Windows

Windows isolates Bluetooth Link Keys under registry keys accessible strictly by the `NT AUTHORITY\SYSTEM` account.

---

## 1. Running the Extraction Script

1. Open Windows Start Menu, type `powershell`.
2. Right-click **Windows PowerShell** and select **Run as Administrator**.
3. Navigate to the repository directory:
   ```powershell
   cd C:\path\to\bt-dualboot
   ```
4. Allow script execution in the current process and run:
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force
   .\windows\Export-BluetoothKeys.ps1
   ```

---

## 2. Custom Output Path

You can specify where to write the JSON file:

```powershell
.\windows\Export-BluetoothKeys.ps1 -OutputPath "D:\Shared\btkeys.json"
```

---

## 3. What Happens Under the Hood?

1. **Elevation Verification**: Validates that PowerShell is running in an elevated Administrator session.
2. **Ephemeral Task Provisioning**: Registers a temporary scheduled task named `BTDualBoot_ExportKeys_<Random>` running under the `NT AUTHORITY\SYSTEM` identity.
3. **Registry Export**: Dumps `HKLM\SYSTEM\CurrentControlSet\Services\BTHPORT\Parameters\Keys` to a temporary file.
4. **Friendly Name Resolution**: Reads `HKLM\SYSTEM\CurrentControlSet\Services\BTHPORT\Parameters\Devices` and the Windows PnP cache to pair each hex MAC address with human-readable names (e.g., Logitech MX Master 3).
5. **Zero-Residual Cleanup**: In a strict `finally` block:
   - Destroys the scheduled task.
   - Deletes the temporary `.reg` export.
   - Writes clean, sanitized JSON to `btkeys.json`.
