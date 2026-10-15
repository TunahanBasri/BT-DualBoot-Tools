# 🚀 BT-DualBoot Tools (v1.0.0)

<p align="center">
  <b>Seamless Bluetooth Key Synchronization for Windows & Linux Dual-Boot Setups</b><br>
  <i>Stop re-pairing your Bluetooth mouse, keyboard, and headphones every time you switch operating systems.</i>
</p>

<p align="center">
  <a href="https://github.com/TunahanBasri/bt-dualboot-tools/releases"><img src="https://img.shields.io/badge/Release-v1.0.0-blue.svg?style=flat-square" alt="Release v1.0.0"></a>
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-brightgreen.svg?style=flat-square" alt="Platform">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green.svg?style=flat-square" alt="License MIT"></a>
  <img src="https://img.shields.io/badge/Tests-30%20Passed-success.svg?style=flat-square" alt="Tests Passed">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue.svg?style=flat-square" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/Dependencies-Zero-purple.svg?style=flat-square" alt="Zero Dependencies">
  <a href="#-sponsor--support"><img src="https://img.shields.io/badge/Sponsor-%E2%99%A5-pink.svg?style=flat-square" alt="Sponsor Project"></a>
</p>

> 📖 **Kullanıcı Kılavuzları / Manuals:**
> - 🇹🇷 **[Türkçe Kolay Kullanım Kılavuzu](KULLANIM_KILAVUZU.md)**: 3 adımda kolay eşleştirme ve acemi rehberi.
> - 🌐 **[English Operating Manual](USER_MANUAL_EN.md)**: Concise step-by-step operating procedure for English speakers.

---

## 💡 The Problem & The Solution

### ❌ The Pain Point
If you dual-boot **Windows** and **Linux** on the same machine, you know the chronic frustration:
Every time you switch operating systems, **your Bluetooth mouse and keyboard stop working**. 
Because each OS negotiates a distinct cryptographic Link Key with the device during pairing, pairing on Windows invalidates the connection on Linux, and pairing on Linux breaks Windows. You are stuck repeatedly re-pairing your peripherals on every single reboot.

### ✨ The Solution
**BT-DualBoot Tools** permanently eliminates this friction:
1. **Windows**: Safely extracts the cryptographic pairing keys directly from the protected Windows kernel registry (`BTHPORT`) using native, ephemeral `NT AUTHORITY\SYSTEM` elevation.
2. **Linux**: Automatically injects these keys into the BlueZ configuration files (`/var/lib/bluetooth`), creates an instant snapshot backup for rollback safety, and restarts the Bluetooth daemon.
3. **Result**: Your Bluetooth devices connect seamlessly on **both** Windows and Linux without ever touching the pairing button again!

---

## ⚡ Terminal Demo Preview

```text
+--------------------------------------------------------------+
|                BT-DualBoot Tools v1.0.0                         |
|   Seamless Bluetooth Key Sync Between Windows and Linux (BlueZ)|
+--------------------------------------------------------------+

>>> SIMULATION MODE (--dry-run): No files will be modified <<<

Synchronization Plan:
Device Name              Device MAC         Status             Details
---------------------------------------------------------------------------
Logitech MX Master 3     54:46:6b:00:09:fb  WILL UPDATE        Key: 1111...1111 -> 5885...4FD6
Keychron K2 Mechanical   f4:4e:fc:21:44:a8  WILL UPDATE        New [LinkKey] section
---------------------------------------------------------------------------
Summary: 0 already synced, 2 to update, 0 not found in Linux

[*] Creating automatic BlueZ configuration backup...
[SUCCESS] Snapshot saved to: /var/lib/bluetooth_backup_20261015_013000
 [OK] Updated Logitech MX Master 3 (54:46:6b:00:09:fb)
 [OK] Updated Keychron K2 Mechanical (f4:4e:fc:21:44:a8)
[*] Reloading Bluetooth service...
[SUCCESS] Bluetooth service restarted successfully.

[DONE] Successfully synchronized 2 device(s)!
```

---

## 🚀 Quickstart Guide (2 Steps • 30 Seconds)

```
[ Windows ]                                 [ Linux ]
  Double-Click Export-Keys.bat                 sudo python sync.py
 ┌─────────────────────────┐                 ┌────────────────────────┐
 │     Export-Keys.bat     │ ──btkeys.json─> │   sudo python sync.py  │
 └─────────────────────────┘                 └────────────────────────┘
                                                         │
                                                         ▼
                                                 Bluetooth Ready! 🎉
```

> [!TIP]
> **First-time setup tip:** Ensure your Bluetooth keyboard/mouse has been paired in Linux at least once. This creates the device profile under `/var/lib/bluetooth`.

### Step 1: Export Keys in Windows
1. Pair your Bluetooth devices in Windows settings normally.
2. Double-click **`Export-Keys.bat`** (or run `.\windows\Export-BluetoothKeys.ps1` in PowerShell as Admin).
3. A clean `btkeys.json` file will appear in your folder. Copy it to your Linux drive or flash drive.

### Step 2: Sync in Linux
1. Boot into **Linux**.
2. Run the interactive sync helper:
   ```bash
   sudo python sync.py
   ```
   *(Or if you prefer the CLI: `sudo bt-dualboot btkeys.json` or `sudo python -m bt_dualboot.cli btkeys.json --dry-run`)*
3. **Done!** Classic & BLE cryptographic keys (with automatic Little-Endian Rand/EDiv reversal) are instantly injected into BlueZ. Your keyboard and mouse connect immediately without ever needing re-pairing!

---

## 📊 Comparison & Benchmarks

| Feature / Metric | 🔄 Re-Pairing Each Boot | 🛠️ Offline Disk Mount | 📦 Third-Party Binaries | 🚀 **BT-DualBoot Tools** |
| :--- | :--- | :--- | :--- | :--- |
| **Time per Switch** | 2 - 5 Minutes | 10 - 20 Minutes | 3 - 5 Minutes | **< 2 Seconds** |
| **External Dependencies** | None | Raw NTFS drivers / parsers | External runtimes | **Zero (Native OS tools only)** |
| **Disk / OS Integrity** | Safe | Potential dirty bit / fast startup issue | Varies | **Safe (Native read-only API)** |
| **Device Friendly Names** | Manual guesswork | Raw MAC only | Raw MAC only | **Automatic resolution** |
| **Simulation Mode** | ❌ No | ❌ No | ❌ No | **✅ Yes (`--dry-run`)** |
| **Instant Rollback** | ❌ No | ❌ Manual | ❌ Manual | **✅ Yes (`--rollback`)** |
| **Key Privacy** | N/A | Plaintext | Plaintext | **✅ Masked by default (`5885...4FD6`)** |
| **Accessibility & CI** | N/A | N/A | N/A | **✅ `NO_COLOR` / `--no-color` compliant** |
| **Test Coverage** | None | None | Unknown | **30 Unit & Persona Tests (100% Pass)** |

---

## 📚 Documentation & Technical Guides

Comprehensive engineering documentation organized by operational use case:

| Quadrant | Focus | Guides & References |
| :--- | :--- | :--- |
| **Tutorials** | Learning | [Quickstart Guide](docs/tutorials/quickstart.md) |
| **How-To Guides** | Problem-Solving | [Sync Devices](docs/how-to/sync-devices.md) • [Rollback & Recovery](docs/how-to/rollback-backup.md) • [Windows Extraction](docs/how-to/windows-key-extraction.md) |
| **Reference** | Information | [CLI Options](docs/reference/cli-options.md) • [Key Formats & Schema](docs/reference/key-formats-schema.md) • [Exit Codes](docs/reference/exit-codes.md) |
| **Explanation** | Understanding | [System Architecture Flow](docs/Architecture.md) • [Bluetooth Cryptography](docs/explanation/bluetooth-cryptography.md) • [Windows Security](docs/explanation/windows-system-security.md) • [BlueZ Architecture](docs/explanation/linux-bluez-architecture.md) |

### 🏛️ Architectural Decision Records (MADR v4.0)
Key engineering choices are documented in `docs/decisions/`:
- [ADR 0001: Ephemeral Scheduled Task for Windows SYSTEM Elevation](docs/decisions/0001-ephemeral-system-task.md)
- [ADR 0002: Non-Destructive INI Stream Parser](docs/decisions/0002-nondestructive-ini-parser.md)
- [ADR 0003: Zero External Dependencies Policy](docs/decisions/0003-zero-external-dependencies.md)

---

## 💖 Sponsor & Support

This project is built and maintained as a free, independent open-source tool for the dual-boot community. If BT-DualBoot saved you hours of re-pairing frustration, please consider supporting ongoing development:

- **GitHub Sponsors**: [github.com/sponsors/TunahanBasri](https://github.com/sponsors/TunahanBasri)

Every sponsorship fuels maintenance, testing on new Linux kernels, and BLE (Bluetooth Low Energy) roadmap progress!

---

## 📄 License & Contributing

This project is licensed under the permissive **MIT License** - see the [LICENSE](LICENSE) file for details.
- 100% Free and Open-Source software.
- AI Search & Indexing Friendly: Freely indexed so AI assistants (ChatGPT, Copilot, Claude, Gemini) and search engines can recommend it to users facing dual-boot friction.

Contributions are warmly welcomed! Please review [CONTRIBUTING.md](CONTRIBUTING.md) before submitting pull requests.
