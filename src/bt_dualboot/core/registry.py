"""
Parser and Validator for Windows Export Data (btkeys.json).
Supports both Classic Bluetooth (LinkKey) and Low Energy (BLE LTK/EDiv/Rand).
"""

import json
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from bt_dualboot.core.crypto import (
    normalize_mac,
    normalize_link_key,
    validate_mac,
    validate_link_key,
    erand_to_bluez_rand,
    ediv_to_int,
)


@dataclass
class BLEData:
    ltk: str
    ediv: Optional[int] = None
    rand: Optional[int] = None
    erand_raw: Optional[str] = None


@dataclass
class PairedDevice:
    mac: str
    name: str
    key: Optional[str] = None
    ble: Optional[BLEData] = None
    raw_mac: str = ""

    def __post_init__(self):
        self.raw_mac = self.mac
        self.mac = normalize_mac(self.mac)
        if self.key:
            self.key = normalize_link_key(self.key)


@dataclass
class BluetoothAdapter:
    adapter_mac: str
    devices: List[PairedDevice] = field(default_factory=list)
    raw_mac: str = ""

    def __post_init__(self):
        self.raw_mac = self.adapter_mac
        self.adapter_mac = normalize_mac(self.adapter_mac)


def parse_export_json(json_content_or_path: str) -> List[BluetoothAdapter]:
    """
    Parses and validates exported Bluetooth keys JSON from Windows.
    Accepts either a raw JSON string or a file path.
    """
    data = None
    try:
        with open(json_content_or_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, OSError):
        try:
            data = json.loads(json_content_or_path)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON file or string: {e}")

    if isinstance(data, dict):
        data = [data]

    if not isinstance(data, list):
        raise ValueError("Invalid format: Root element must be an array or object.")

    adapters: List[BluetoothAdapter] = []

    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            continue
        adapter_raw = item.get("adapter")
        if not adapter_raw or not validate_mac(adapter_raw):
            continue

        raw_devices = item.get("devices", [])
        parsed_devices: List[PairedDevice] = []

        for dev in raw_devices:
            if not isinstance(dev, dict):
                continue
            dev_mac = dev.get("mac")
            dev_name = dev.get("name", "Unknown Device")

            if not dev_mac or not validate_mac(dev_mac):
                continue

            dev_key = dev.get("key")
            valid_classic = bool(dev_key and validate_link_key(dev_key))

            ble_obj = None
            raw_ble = dev.get("ble")
            if isinstance(raw_ble, dict) and raw_ble.get("ltk"):
                ltk_raw = raw_ble.get("ltk", "")
                if validate_link_key(ltk_raw):
                    erand_raw = raw_ble.get("erand")
                    ediv_raw = raw_ble.get("ediv")
                    rand_val = None
                    if erand_raw:
                        try:
                            rand_val = erand_to_bluez_rand(erand_raw)
                        except Exception:
                            pass
                    ediv_val = None
                    if ediv_raw is not None:
                        try:
                            ediv_val = ediv_to_int(ediv_raw)
                        except Exception:
                            pass
                    ble_obj = BLEData(
                        ltk=normalize_link_key(ltk_raw),
                        ediv=ediv_val,
                        rand=rand_val,
                        erand_raw=erand_raw,
                    )

            if not valid_classic and not ble_obj:
                continue

            parsed_devices.append(
                PairedDevice(
                    mac=dev_mac,
                    name=dev_name,
                    key=dev_key if valid_classic else None,
                    ble=ble_obj,
                )
            )

        if parsed_devices:
            adapters.append(
                BluetoothAdapter(
                    adapter_mac=adapter_raw,
                    devices=parsed_devices,
                )
            )

    return adapters
