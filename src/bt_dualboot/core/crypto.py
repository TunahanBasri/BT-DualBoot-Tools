"""
Cryptographic and Byte Manipulation Utilities for Bluetooth Dual-Boot Synchronization.
"""

import re
from typing import Optional


def normalize_mac(mac: str) -> str:
    """
    Normalizes a MAC address into standard lowercase colon-delimited format.
    Example: '54466B0009FB' -> '54:46:6b:00:09:fb'
             '54-46-6B-00-09-FB' -> '54:46:6b:00:09:fb'
    """
    clean = re.sub(r"[^0-9a-fA-F]", "", mac).lower()
    if len(clean) != 12:
        raise ValueError(f"Invalid MAC address format: '{mac}'. Expected 12 hexadecimal characters.")
    return ":".join(clean[i : i + 2] for i in range(0, 12, 2))


def validate_mac(mac: str) -> bool:
    """Check if the provided string is a valid MAC address."""
    clean = re.sub(r"[^0-9a-fA-F]", "", mac)
    return len(clean) == 12


def normalize_link_key(key: str) -> str:
    """
    Normalizes a 128-bit Classic Bluetooth Link Key into a 32-character uppercase hex string.
    Example: '58,85,46,ea...' -> '588546EA82C033CE9508E1C74EC74FD6'
    """
    clean = re.sub(r"[^0-9a-fA-F]", "", key).upper()
    if len(clean) != 32:
        raise ValueError(f"Invalid Link Key length: '{key}'. Expected 32 hex characters (128 bits), got {len(clean)}.")
    return clean


def validate_link_key(key: str) -> bool:
    """Check if the provided string is a valid 128-bit Link Key."""
    clean = re.sub(r"[^0-9a-fA-F]", "", key)
    return len(clean) == 32


# --- BLE (Low Energy) Endianness Utilities (Roadmap v1.1 Foundation) ---


def reverse_endianness_bytes(hex_str: str) -> str:
    """
    Reverses byte order of a hex string (Little-Endian <-> Big-Endian).
    Example: 'AB CD EF 12' -> '12 EF CD AB'
    """
    clean = re.sub(r"[^0-9a-fA-F]", "", hex_str).upper()
    if len(clean) % 2 != 0:
        raise ValueError("Hex string must contain an even number of characters.")
    byte_chunks = [clean[i : i + 2] for i in range(0, len(clean), 2)]
    return "".join(reversed(byte_chunks))


def erand_to_bluez_rand(erand_hex: str) -> int:
    """
    Converts a Windows 64-bit Little-Endian ERand hex string to BlueZ unsigned decimal integer.
    Example:
        Windows ERand: 'ab cd ef 12 34 56 78 90' (8 bytes)
        Big-Endian Hex: '9078563412efcdab'
        BlueZ Rand (decimal): 10411030018809425323
    """
    clean = re.sub(r"[^0-9a-fA-F]", "", erand_hex)
    if len(clean) != 16:
        raise ValueError(f"Expected 8 bytes (16 hex chars) for ERand, got {len(clean)}.")
    be_hex = reverse_endianness_bytes(clean)
    return int(be_hex, 16)


def ediv_to_int(ediv_val) -> int:
    """
    Normalizes Windows EDiv (REG_DWORD or hex string) to 16-bit decimal integer.
    """
    if isinstance(ediv_val, int):
        return ediv_val & 0xFFFF
    clean = re.sub(r"[^0-9a-fA-F]", "", str(ediv_val))
    return int(clean, 16) & 0xFFFF
