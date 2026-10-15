# Bluetooth Cryptography & Key Management 🔐

This document explains the cryptographic fundamentals of Bluetooth device pairing, comparing **Bluetooth Classic** and **Bluetooth Low Energy (BLE)**, and detailing why specific data transformations are necessary between Windows and Linux.

---

## 1. The Core Problem: Why Dual-Boot Breaks Bluetooth

When a Bluetooth peripheral (such as a mouse, keyboard, or headphones) pairs with a computer, the device and the host exchange encryption secrets and generate a shared pairing key.

1. When you boot into **Windows** and pair your mouse, Windows generates Key `A` and stores it.
2. When you reboot into **Linux** and pair the mouse, Linux generates Key `B` and overwrites the key on the mouse.
3. When you reboot back into **Windows**, Windows tries to authenticate with Key `A`, but the mouse now expects Key `B`.
4. Authentication fails -> Connection drops -> You are forced to re-pair the device every single time you reboot!

**The Solution**: Make both operating systems use the exact same pairing key!

---

## 2. Bluetooth Classic (v1.0.0 Supported)

- **Pairing Architecture**: Legacy PIN or Secure Simple Pairing (SSP) based on Elliptic Curve Diffie-Hellman (P-192 / P-256).
- **Primary Secret**: A single 128-bit **Link Key**.
- **Storage in Windows**: Stored in registry under `BTHPORT\Parameters\Keys\<AdapterMAC>\<DeviceMAC>`.
- **Storage in Linux (BlueZ)**: Stored in `/var/lib/bluetooth/<AdapterMAC>/<DeviceMAC>/info` under section `[LinkKey]`:
  ```ini
  [LinkKey]
  Key=588546EA82C033CE9508E1C74EC74FD6
  Type=0
  PINLength=0
  ```
- **Conversion Complexity**: Low. The 16-byte raw binary array in the Windows registry directly maps to BlueZ's uppercase 32-character hexadecimal format.

---

## 3. Bluetooth Low Energy (BLE) (Roadmap v1.1)

Modern Bluetooth Low Energy devices (such as Apple Magic Mouse, modern Bluetooth 5.x peripherals) do not use a single LinkKey. Instead, they utilize a key hierarchy:
- **Long Term Key (LTK)**: 128-bit secret used for link layer encryption.
- **Encrypted Diversifier (EDiv)**: 16-bit integer used by the peripheral to look up the LTK.
- **Randomizer (ERand / Rand)**: 64-bit random value provided by the peripheral during initial pairing.

### Endianness & Format Discrepancies (Why Simple Copy-Paste Fails for BLE)

| Parameter | Windows Registry Storage | Linux BlueZ INI Format |
| :--- | :--- | :--- |
| **LTK** | `REG_BINARY` (16 bytes) | 32-char Hexadecimal String |
| **EDiv** | `REG_DWORD` (Little-Endian Hex) | 16-bit Decimal Integer (e.g., `48215`) |
| **ERand / Rand** | `REG_BINARY` (8 bytes, Little-Endian) | 64-bit Unsigned Decimal (Big-Endian) |

### The Conversion Algorithm for BLE Rand:
1. Extract the raw 8-byte `ERand` array from the Windows Registry:
   ```
   [ 0xAB, 0xCD, 0xEF, 0x12, 0x34, 0x56, 0x78, 0x90 ]
   ```
2. Reverse the byte sequence from Little-Endian to Big-Endian:
   ```
   [ 0x90, 0x78, 0x56, 0x34, 0x12, 0xEF, 0xCD, 0xAB ]
   ```
3. Form the Big-Endian hexadecimal representation:
   `"9078563412EFCDAB"`
4. Convert to an unsigned 64-bit decimal integer:
   `10410165320322895275`
5. Write into BlueZ `info`:
   ```ini
   [LongTermKey]
   Key=...
   EDiv=48215
   Rand=10410165320322895275
   ```
