"""
Linux BlueZ Configuration Parser, Updater, and Syncer.
Manipulates /var/lib/bluetooth config files without breaking formatting or existing properties.
Supports both Classic Bluetooth (LinkKey) and Low Energy (LongTermKey with Rand/EDiv).
"""

import os
import subprocess
from dataclasses import dataclass
from typing import Optional, List, Dict, Tuple, Any
from bt_dualboot.core.crypto import normalize_mac


@dataclass
class DeviceSyncPlan:
    adapter_mac: str
    device_mac: str
    device_name: str
    info_path: str
    status: str  # 'WILL_UPDATE', 'ALREADY_SYNCED', 'DEVICE_NOT_FOUND', 'ADAPTER_NOT_FOUND', 'INFO_MISSING'
    old_key: Optional[str] = None
    new_key: Optional[str] = None
    ble_data: Optional[Any] = None
    message: str = ""


def find_adapter_dir(base_path: str, adapter_mac: str) -> Optional[str]:
    """Find matching adapter directory in BlueZ storage (case-insensitive)."""
    if not os.path.exists(base_path):
        return None

    target = normalize_mac(adapter_mac)
    target_uncol = target.replace(":", "")

    for entry in os.listdir(base_path):
        clean_entry = entry.lower().strip()
        if clean_entry == target or clean_entry == target_uncol:
            full_path = os.path.join(base_path, entry)
            if os.path.isdir(full_path):
                return full_path
    return None


def find_device_dir(adapter_path: str, device_mac: str) -> Optional[str]:
    """Find matching device directory inside adapter directory."""
    if not os.path.exists(adapter_path):
        return None

    target = normalize_mac(device_mac)
    target_uncol = target.replace(":", "")

    for entry in os.listdir(adapter_path):
        clean_entry = entry.lower().strip()
        if clean_entry == target or clean_entry == target_uncol:
            full_path = os.path.join(adapter_path, entry)
            if os.path.isdir(full_path):
                return full_path
    return None


def parse_info_file(info_path: str) -> Tuple[List[str], Optional[str], bool]:
    """
    Reads an info file and extracts:
    - lines: list of original lines
    - current_key: existing LinkKey if present
    - has_link_key_section: bool
    """
    if not os.path.exists(info_path):
        return [], None, False

    with open(info_path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    current_section = None
    current_key = None
    has_link_key_section = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            current_section = stripped[1:-1]
            if current_section == "LinkKey":
                has_link_key_section = True
            continue

        if current_section == "LinkKey" and "=" in stripped:
            k, v = stripped.split("=", 1)
            if k.strip().lower() == "key":
                current_key = v.strip().upper()

    return lines, current_key, has_link_key_section


def generate_updated_info(
    lines: List[str],
    new_key: Optional[str] = None,
    has_link_key_section: bool = False,
    ble_data: Optional[Any] = None,
) -> List[str]:
    """
    Generates updated lines for the info file, updating or appending [LinkKey] and [LongTermKey]
    while preserving other sections and comments.
    """
    new_lines: List[str] = []
    current_section = None
    key_written = False

    # 1. Update Classic LinkKey
    if new_key:
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("[") and stripped.endswith("]"):
                current_section = stripped[1:-1]
                new_lines.append(line)
                continue

            if current_section == "LinkKey" and "=" in line:
                parts = line.split("=", 1)
                if parts[0].strip().lower() == "key":
                    new_lines.append(f"Key={new_key}\n")
                    key_written = True
                    continue

            new_lines.append(line)

        if not has_link_key_section:
            if new_lines and not new_lines[-1].endswith("\n"):
                new_lines[-1] += "\n"
            new_lines.append("\n[LinkKey]\n")
            new_lines.append(f"Key={new_key}\n")
            new_lines.append("Type=0\n")
            new_lines.append("PINLength=0\n")
        elif not key_written and has_link_key_section:
            idx = -1
            for i, l in enumerate(new_lines):
                if l.strip() == "[LinkKey]":
                    idx = i
                    break
            if idx != -1:
                new_lines.insert(idx + 1, f"Key={new_key}\n")
    else:
        new_lines = list(lines)

    # 2. Update BLE LongTermKey if present
    if ble_data and hasattr(ble_data, "ltk") and ble_data.ltk:
        final_lines: List[str] = []
        in_ltk = False
        has_ltk = False
        written_props = set()

        for line in new_lines:
            stripped = line.strip()
            if stripped.startswith("[") and stripped.endswith("]"):
                if in_ltk:
                    if "Key" not in written_props:
                        final_lines.append(f"Key={ble_data.ltk}\n")
                    if "EDiv" not in written_props and ble_data.ediv is not None:
                        final_lines.append(f"EDiv={ble_data.ediv}\n")
                    if "Rand" not in written_props and ble_data.rand is not None:
                        final_lines.append(f"Rand={ble_data.rand}\n")
                    in_ltk = False

                sec_name = stripped[1:-1]
                if sec_name == "LongTermKey":
                    has_ltk = True
                    in_ltk = True
                final_lines.append(line)
                continue

            if in_ltk and "=" in line:
                k, v = line.split("=", 1)
                prop = k.strip()
                if prop.lower() == "key":
                    final_lines.append(f"Key={ble_data.ltk}\n")
                    written_props.add("Key")
                    continue
                elif prop.lower() == "ediv" and ble_data.ediv is not None:
                    final_lines.append(f"EDiv={ble_data.ediv}\n")
                    written_props.add("EDiv")
                    continue
                elif prop.lower() == "rand" and ble_data.rand is not None:
                    final_lines.append(f"Rand={ble_data.rand}\n")
                    written_props.add("Rand")
                    continue

            final_lines.append(line)

        if in_ltk:
            if "Key" not in written_props:
                final_lines.append(f"Key={ble_data.ltk}\n")
            if "EDiv" not in written_props and ble_data.ediv is not None:
                final_lines.append(f"EDiv={ble_data.ediv}\n")
            if "Rand" not in written_props and ble_data.rand is not None:
                final_lines.append(f"Rand={ble_data.rand}\n")

        if not has_ltk:
            if final_lines and not final_lines[-1].endswith("\n"):
                final_lines[-1] += "\n"
            final_lines.append("\n[LongTermKey]\n")
            final_lines.append(f"Key={ble_data.ltk}\n")
            final_lines.append("Authenticated=0\n")
            final_lines.append("EncSize=16\n")
            if ble_data.ediv is not None:
                final_lines.append(f"EDiv={ble_data.ediv}\n")
            if ble_data.rand is not None:
                final_lines.append(f"Rand={ble_data.rand}\n")

        return final_lines

    return new_lines


def plan_device_sync(
    base_path: str,
    adapter_mac: str,
    device_mac: str,
    device_name: str,
    new_key: Optional[str] = None,
    ble_data: Optional[Any] = None,
) -> DeviceSyncPlan:
    """Prepares an inspection plan for a single device without writing changes."""
    norm_adapter = normalize_mac(adapter_mac)
    norm_device = normalize_mac(device_mac)

    adapter_path = find_adapter_dir(base_path, norm_adapter)
    if not adapter_path:
        return DeviceSyncPlan(
            adapter_mac=norm_adapter,
            device_mac=norm_device,
            device_name=device_name,
            info_path="",
            status="ADAPTER_NOT_FOUND",
            message=f"Adapter {norm_adapter} not found in {base_path}",
        )

    device_path = find_device_dir(adapter_path, norm_device)
    if not device_path:
        return DeviceSyncPlan(
            adapter_mac=norm_adapter,
            device_mac=norm_device,
            device_name=device_name,
            info_path="",
            status="DEVICE_NOT_FOUND",
            message="Device directory not found. Please pair device once in Linux first.",
        )

    info_path = os.path.join(device_path, "info")
    if not os.path.exists(info_path):
        return DeviceSyncPlan(
            adapter_mac=norm_adapter,
            device_mac=norm_device,
            device_name=device_name,
            info_path=info_path,
            status="INFO_MISSING",
            message=f"Device info file missing at {info_path}",
        )

    lines, current_key, has_section = parse_info_file(info_path)

    # Check sync status
    is_synced = False
    if new_key and current_key and current_key.upper() == new_key.upper():
        is_synced = True

    if is_synced and not ble_data:
        return DeviceSyncPlan(
            adapter_mac=norm_adapter,
            device_mac=norm_device,
            device_name=device_name,
            info_path=info_path,
            status="ALREADY_SYNCED",
            old_key=current_key,
            new_key=new_key,
            ble_data=ble_data,
            message="Pairing keys already match.",
        )

    return DeviceSyncPlan(
        adapter_mac=norm_adapter,
        device_mac=norm_device,
        device_name=device_name,
        info_path=info_path,
        status="WILL_UPDATE",
        old_key=current_key,
        new_key=new_key,
        ble_data=ble_data,
        message="Key will be updated.",
    )


def apply_device_sync(plan: DeviceSyncPlan) -> bool:
    """Writes updated keys to disk atomically according to the sync plan."""
    if plan.status != "WILL_UPDATE":
        return False

    lines, current_key, has_section = parse_info_file(plan.info_path)
    new_lines = generate_updated_info(lines, plan.new_key, has_section, plan.ble_data)

    dir_name = os.path.dirname(plan.info_path)
    temp_file = os.path.join(dir_name, f".info.tmp.{os.getpid()}")
    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        if os.name != "nt":
            try:
                os.chmod(temp_file, 0o600)
            except OSError:
                pass
        os.replace(temp_file, plan.info_path)
        return True
    except Exception:
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except OSError:
                pass
        return False


def restart_bluetooth_service() -> Tuple[bool, str]:
    """Restarts BlueZ daemon via systemctl."""
    try:
        res = subprocess.run(["systemctl", "restart", "bluetooth"], check=True, capture_output=True, text=True)
        return True, "Bluetooth service restarted successfully."
    except FileNotFoundError:
        return False, "systemctl command not found (non-systemd Linux distribution)."
    except subprocess.CalledProcessError as e:
        return False, f"Failed to restart bluetooth service: {e.stderr or e}"
    except Exception as e:
        return False, f"Unexpected error restarting service: {e}"


def check_connected_devices() -> List[str]:
    """Queries bluetoothctl to check which devices are actively connected."""
    try:
        res = subprocess.run(["bluetoothctl", "devices", "Connected"], capture_output=True, text=True, timeout=3)
        if res.returncode == 0:
            lines = res.stdout.strip().splitlines()
            connected = []
            for line in lines:
                parts = line.strip().split(maxsplit=2)
                if len(parts) >= 2 and parts[0] == "Device":
                    connected.append(parts[1].lower())
            return connected
    except Exception:
        pass
    return []


def list_installed_bluez_devices(base_path: str = "/var/lib/bluetooth") -> List[Dict[str, str]]:
    """
    Scans BlueZ base directory and returns list of already paired devices on Linux.
    Each item: {"adapter": "...", "device": "...", "name": "...", "info_path": "..."}
    """
    results = []
    if not os.path.exists(base_path) or not os.path.isdir(base_path):
        return results

    try:
        adapters = os.listdir(base_path)
    except OSError:
        return results

    for adapter_entry in adapters:
        adapter_path = os.path.join(base_path, adapter_entry)
        if not os.path.isdir(adapter_path) or adapter_entry == "backups":
            continue

        try:
            device_entries = os.listdir(adapter_path)
        except OSError:
            continue

        for dev_entry in device_entries:
            dev_path = os.path.join(adapter_path, dev_entry)
            info_file = os.path.join(dev_path, "info")
            if os.path.isfile(info_file):
                dev_name = dev_entry
                try:
                    with open(info_file, "r", encoding="utf-8", errors="replace") as f:
                        for line in f:
                            if line.strip().startswith("Name="):
                                dev_name = line.strip().split("=", 1)[1].strip()
                                break
                except OSError:
                    pass

                results.append({
                    "adapter": adapter_entry,
                    "device": dev_entry,
                    "name": dev_name,
                    "info_path": info_file,
                })

    return results

