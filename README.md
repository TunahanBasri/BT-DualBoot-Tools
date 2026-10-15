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
+-----------------------------------------------------------------+
|                    BT-DualBoot Tools v1.0.0                     |
|  Seamless Bluetooth Key Sync Between Windows and Linux (BlueZ)  |
+-----------------------------------------------------------------+

Synchronization Plan:
Device Name              Device MAC         Status             Details
---------------------------------------------------------------------------
Sony WH-1000XM4          38:18:4c:82:11:04  WILL UPDATE        Key: 1111...1111 -> 5885...4FD6
Keychron K2 Mechanical   f4:4e:fc:21:44:a8  WILL UPDATE        New [LinkKey] section
---------------------------------------------------------------------------
Summary: 0 already synced, 2 to update, 0 not found in Linux

[*] Creating automatic BlueZ configuration backup...
[SUCCESS] Snapshot saved to: /var/lib/bluetooth_backup_20261015_013000
 [OK] Updated Sony WH-1000XM4 (38:18:4c:82:11:04)
 [OK] Updated Keychron K2 Mechanical (f4:4e:fc:21:44:a8)
[*] Reloading Bluetooth service...
[SUCCESS] Bluetooth service restarted successfully.

[DONE] Successfully synchronized 2 device(s)!
```

---

## 🚀 Quickstart Guide (3 Simple Steps)

```
[ Step 1: Linux ]                     [ Step 2: Windows ]                     [ Step 3: Linux ]
Pair device in Settings              1. Pair device in Settings              1. Run sudo python sync.py
(Creates BlueZ profile)      ──►     2. Double-click Export-Keys.bat ──►     2. Drag & drop btkeys.json
                                     3. Send btkeys.json to Linux            🎉 Bluetooth Connected!
```

> [!TIP]
> **Why this order?** Bluetooth peripherals only store the *single most recent key*. Pairing in Linux first creates the device hardware folder in BlueZ. Pairing in Windows second negotiates the latest active key. The sync script then copies this key to Linux!

### Step 1: Pair in Linux First (Zero Point)
1. Boot into **Linux**.
2. Open Bluetooth Settings and pair your mouse/keyboard normally.
3. Confirm the device works. *(Linux creates the internal profile under `/var/lib/bluetooth`).*

### Step 2: Pair & Export in Windows
1. Reboot into **Windows**.
2. Open Bluetooth Settings and pair the same mouse/keyboard. *(Windows writes the newest key into the device).*
3. Double-click **`Export-Keys.bat`** (or run `.\windows\Export-BluetoothKeys.ps1` in PowerShell as Admin).
4. A clean `btkeys.json` file will appear in your project folder.
5. **Transfer `btkeys.json` to Linux using whatever method is easiest for you:**
   - 💬 **Method A (No USB needed • Messaging / Cloud):** Send `btkeys.json` to yourself via WhatsApp Web, Telegram Saved Messages, Google Drive, or Email. Download it in Linux!
   - 📂 **Method B (Direct Disk Access):** Open your Windows `C:\` partition directly from Linux's file manager and grab `btkeys.json`.
   - 💾 **Method C (Traditional USB Drive):** Copy `btkeys.json` onto a USB flash drive.

> [!NOTE]
> 🔒 **Security Best Practice:** Bluetooth Link Keys are cryptographic secrets. If you transfer `btkeys.json` via messaging or cloud (WhatsApp/Telegram/Email), delete the file/message from your chat and downloads once synchronization is complete.

### Step 3: One-Click Sync in Linux
1. Boot back into **Linux**.
2. Open a terminal in the project folder and run:
   ```bash
   sudo python sync.py
   ```
   *(Or if you prefer the CLI: `sudo bt-dualboot btkeys.json` or `sudo python -m bt_dualboot.cli btkeys.json --dry-run`)*
3. Drag and drop your **`btkeys.json`** file directly into the terminal window (or place it in the project folder and press Enter).
4. **Done!** The tool automatically creates a rollback backup, injects pairing keys into BlueZ, and restarts Bluetooth. Your keyboard and mouse connect immediately without ever needing re-pairing!

---

## 📊 Comparison & Benchmarks

| Feature / Metric | 🔄 Re-Pairing Each Boot | 🛠️ Offline Disk Mount | 📦 Third-Party Binaries | 🚀 **BT-DualBoot Tools** |
| :--- | :--- | :--- | :--- | :--- |
| **Time per OS Switch** | 2 - 5 Minutes (every reboot) | Manual remount & sync | 3 - 5 Minutes | **0 Seconds (Instant connection)** |
| **Initial Setup Time** | 0 Minutes | 15 - 30 Minutes | 5 - 10 Minutes | **~3 Minutes (One-time only)** |
| **External Dependencies** | None | Raw NTFS drivers / parsers | External runtimes | **Zero (Native OS tools only)** |
| **Disk / OS Integrity** | Safe | Potential dirty bit / fast startup issue | Varies | **Safe (Native read-only API)** |
| **Device Friendly Names** | Manual guesswork | Raw MAC only | Raw MAC only | **Automatic resolution** |
| **Simulation Mode** | ❌ No | ❌ No | ❌ No | **✅ Yes (`--dry-run`)** |
| **Instant Rollback** | ❌ No | ❌ Manual | ❌ Manual | **✅ Yes (`--rollback`)** |
| **Key Privacy** | N/A | Plaintext | Plaintext | **✅ Masked by default (`5885...4FD6`)** |
| **Accessibility & CI** | N/A | N/A | N/A | **✅ `NO_COLOR` / `--no-color` compliant** |
| **Test Coverage** | None | None | Unknown | **30 Automated Tests (100% Pass)** |

---

## 📚 Documentation & Technical Guides

Comprehensive engineering documentation organized by operational use case:

| Quadrant | Focus | Guides & References |
| :--- | :--- | :--- |
| **Tutorials** | Learning | [Quickstart Guide](docs/tutorials/quickstart.md) |
| **How-To Guides** | Problem-Solving | [Sync Devices](docs/how-to/sync-devices.md) • [Rollback & Recovery](docs/how-to/rollback-backup.md) • [Windows Extraction](docs/how-to/windows-key-extraction.md) |
| **Reference** | Information | [CLI Options](docs/reference/cli-options.md) • [Key Formats & Schema](docs/reference/key-formats-schema.md) • [Exit Codes](docs/reference/exit-codes.md) |
| **Explanation** | Understanding | [System Architecture Flow](docs/Architecture.md) • [Bluetooth Cryptography](docs/explanation/bluetooth-cryptography.md) • [Windows Security](docs/explanation/windows-system-security.md) • [BlueZ Architecture](docs/explanation/linux-bluez-architecture.md) |

### 🏛️ Engineering Decision Records (ADRs)
Key technical choices are documented in `docs/decisions/`:
- [ADR 0001: Ephemeral Scheduled Task for Windows SYSTEM Elevation](docs/decisions/0001-ephemeral-system-task.md)
- [ADR 0002: Non-Destructive INI Stream Parser](docs/decisions/0002-nondestructive-ini-parser.md)
- [ADR 0003: Zero External Dependencies Policy](docs/decisions/0003-zero-external-dependencies.md)

---

## 💖 Sponsor & Support

This project is built and maintained as a free, independent open-source tool for the dual-boot community. If BT-DualBoot saved you hours of re-pairing frustration, please consider supporting ongoing development:

- **GitHub Sponsors**: [github.com/sponsors/TunahanBasri](https://github.com/sponsors/TunahanBasri)

Every sponsorship fuels ongoing maintenance, testing on new Linux kernel releases, and ongoing feature development!

---

## 📄 License & Contributing

This project is licensed under the permissive [MIT License](LICENSE) — see the [LICENSE](LICENSE) file for details.
- 100% Free and Open-Source software.
- Contributions, bug reports, and pull requests are warmly welcomed! Please review [CONTRIBUTING.md](CONTRIBUTING.md) before submitting pull requests.
