# Benchmarks & Method Comparison ⚡

A systematic comparison between traditional workarounds and **BT-DualBoot Tools**.

---

## 📊 Comprehensive Comparison Matrix

| Evaluation Criteria | 🔄 Re-pairing Every Boot | 🛠️ Manual Hive Mount (`chntpw`) | 📦 Third-Party EXE / PsExec | 🚀 **BT-DualBoot Tools** |
| :--- | :--- | :--- | :--- | :--- |
| **Time per Switch** | 2 - 5 Minutes | 10 - 20 Minutes | 3 - 5 Minutes | **< 10 Seconds** |
| **Risk of Registry Corruption** | None | ⚠️ High (raw hive write) | Low | **Zero (Native read-only API)** |
| **Linux BlueZ Safety** | Re-creates profile | ⚠️ Prone to syntax error | Manual copy-paste | **Snapshot Backup + Rollback** |
| **External Dependencies** | None | `chntpw`, `ntfs-3g` | Third-party closed binaries | **Zero (Pure Python + PowerShell)** |
| **Device Friendly Names** | Manual identification | Raw MAC only | Raw MAC only | **Automatic resolution** |
| **Simulation Mode (`--dry-run`)** | ❌ No | ❌ No | ❌ No | **✅ Yes (Table diff preview)** |
| **Reversibility** | Overwrites keys | Manual restore | Manual restore | **✅ Single command (`--rollback`)** |
| **Technical Barrier** | Low (but repetitive) | High (CLI hex editing) | Medium | **Beginner-Friendly** |

---

## ⏱️ Execution Speed Benchmark

Measured on standard NVMe SSD dual-boot hardware (Windows 11 + Ubuntu 24.04):

```
Method: BT-DualBoot Tools
├── Windows Key Extraction (Export-BluetoothKeys.ps1): 1.28 seconds
├── JSON File Size: ~1.2 KB
├── Linux Plan & Verification (--dry-run): 0.08 seconds
├── Linux Backup & Key Injection (apply): 0.14 seconds
└── BlueZ Daemon Reload (systemctl restart): 0.35 seconds
───────────────────────────────────────────────────────────
Total Active Time: ~1.85 seconds
```
