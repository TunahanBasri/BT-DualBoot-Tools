# Explanation: Bluetooth Cryptography & Endianness Conversions 🔐

This document provides in-depth technical analysis of why Bluetooth pairing fails across dual-boot environments and the cryptographic mechanics behind key synchronization.

---

## 1. Why Dual-Boot Breaks Bluetooth Connections

When a Bluetooth peripheral (such as a mouse, keyboard, or headphones) bonds with a host, the two endpoints perform a cryptographic key exchange to establish a shared secret:

1. **First Boot (Windows)**: You pair the mouse. Windows generates Link Key $K_{win}$ and stores it in the local registry. The mouse stores $K_{win}$ in its non-volatile memory (NVRAM).
2. **Second Boot (Linux)**: You boot into Linux. The mouse attempts to authenticate using $K_{win}$, which Linux does not have. You click "Pair" in Linux. Linux generates Link Key $K_{linux}$ and overwrites the mouse's NVRAM secret with $K_{linux}$.
3. **Third Boot (Windows)**: You reboot into Windows. Windows attempts mutual authentication with $K_{win}$. The mouse replies using cryptographic challenges derived from $K_{linux}$. The handshake fails immediately with `Authentication Failure (0x05)`.
4. **Result**: The peripheral cannot connect. You are forced to unpair and re-pair on every single reboot.

### The Solution:
By extracting the exact Link Key generated on one operating system and injecting it into the other, both Windows and Linux authenticate using the exact same shared secret. The peripheral cannot tell that the underlying operating system has changed.

---

## 2. Classic Bluetooth (BR/EDR) Key Architecture

- **Pairing Architecture**: Secure Simple Pairing (SSP) utilizing P-256 Elliptic Curve Diffie-Hellman (ECDH).
- **Core Secret**: A 128-bit **Link Key**.
- **Windows Storage**: Stored as a raw 16-byte binary value under `HKLM\SYSTEM\CurrentControlSet\Services\BTHPORT\Parameters\Keys\<AdapterMAC>\<DeviceMAC>`.
- **Linux Storage**: Stored under `/var/lib/bluetooth/<AdapterMAC>/<DeviceMAC>/info` as a 32-character uppercase hexadecimal string.
- **Conversion**: Direct 1-to-1 byte mapping.

---

## 3. Bluetooth Low Energy (BLE) Roadmap v1.1

Bluetooth Low Energy devices (such as Apple Magic Mouse or modern BLE 5.x peripherals) do not use a single Link Key. Instead, they exchange a parameter hierarchy:

| Parameter | Windows Representation | BlueZ Representation | Transformation Required |
| :--- | :--- | :--- | :--- |
| **LTK** (Long Term Key) | `REG_BINARY` (16 bytes) | 32-char Hex string | Direct string format |
| **EDiv** (Encrypted Diversifier) | `REG_DWORD` (16-bit little-endian) | Decimal integer | `int(ediv_hex, 16)` |
| **ERand** (Randomizer) | `REG_BINARY` (8 bytes, Little-Endian) | 64-bit Unsigned Decimal | **Byte Reversal + Hex-to-Decimal** |

### BLE Byte Reversal & Base Conversion Algorithm:
```
1. Windows Registry ERand (Little-Endian 8 bytes):
   [ 0xAB, 0xCD, 0xEF, 0x12, 0x34, 0x56, 0x78, 0x90 ]

2. Reversal to Big-Endian:
   [ 0x90, 0x78, 0x56, 0x34, 0x12, 0xEF, 0xCD, 0xAB ]

3. Hex String:
   "9078563412EFCDAB"

4. BlueZ Decimal Unsigned 64-bit:
   10411030018809425323
```
This transformation is implemented in `bt_dualboot.core.crypto.erand_to_bluez_rand()`.
