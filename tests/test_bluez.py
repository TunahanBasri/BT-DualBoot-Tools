import os
import tempfile
try:
    import pytest
except ImportError:
    pytest = None
from bt_dualboot.core.bluez import (
    find_adapter_dir,
    find_device_dir,
    parse_info_file,
    generate_updated_info,
    plan_device_sync,
    apply_device_sync,
)


SAMPLE_INFO_WITH_LINKKEY = """[General]
Name=Logitech MX Master 3
Class=0x000580
SupportedTechnologies=BR/EDR;
Trusted=true
Blocked=false

[LinkKey]
Key=11111111222222223333333344444444
Type=0
PINLength=0
"""

SAMPLE_INFO_WITHOUT_LINKKEY = """[General]
Name=Keychron K2
Class=0x002540
SupportedTechnologies=BR/EDR;
Trusted=true
"""


def test_parse_info_file(tmp_path):
    info_file = tmp_path / "info"
    info_file.write_text(SAMPLE_INFO_WITH_LINKKEY, encoding="utf-8")

    lines, current_key, has_section = parse_info_file(str(info_file))
    assert has_section is True
    assert current_key == "11111111222222223333333344444444"
    assert len(lines) > 0


def test_generate_updated_info_replace():
    lines = SAMPLE_INFO_WITH_LINKKEY.splitlines(keepends=True)
    new_key = "588546EA82C033CE9508E1C74EC74FD6"
    updated = generate_updated_info(lines, new_key, has_link_key_section=True)

    updated_text = "".join(updated)
    assert f"Key={new_key}\n" in updated_text
    assert "11111111222222223333333344444444" not in updated_text
    assert "[General]" in updated_text


def test_generate_updated_info_append():
    lines = SAMPLE_INFO_WITHOUT_LINKKEY.splitlines(keepends=True)
    new_key = "588546EA82C033CE9508E1C74EC74FD6"
    updated = generate_updated_info(lines, new_key, has_link_key_section=False)

    updated_text = "".join(updated)
    assert "[LinkKey]" in updated_text
    assert f"Key={new_key}\n" in updated_text
    assert "Type=0\n" in updated_text


def test_plan_and_apply_sync(tmp_path):
    # Setup mock BlueZ filesystem
    # On Windows NTFS, colons are forbidden in directory names, so use uncoloned format
    adapter_name = "4c034fe0d1b0" if os.name == "nt" else "4c:03:4f:e0:d1:b0"
    device_name = "54466b0009fb" if os.name == "nt" else "54:46:6b:00:09:fb"

    adapter_dir = tmp_path / adapter_name
    device_dir = adapter_dir / device_name
    device_dir.mkdir(parents=True)

    info_file = device_dir / "info"
    info_file.write_text(SAMPLE_INFO_WITH_LINKKEY, encoding="utf-8")

    adapter_mac = "4C:03:4F:E0:D1:B0"
    device_mac = "54:46:6B:00:09:FB"
    new_key = "588546EA82C033CE9508E1C74EC74FD6"

    # Step 1: Plan sync (should detect update needed)
    plan = plan_device_sync(str(tmp_path), adapter_mac, device_mac, "Mouse", new_key)
    assert plan.status == "WILL_UPDATE"
    assert plan.old_key == "11111111222222223333333344444444"
    assert plan.new_key == new_key

    # Step 2: Apply sync
    assert apply_device_sync(plan) is True

    # Step 3: Verify plan again (should now be already synced)
    plan2 = plan_device_sync(str(tmp_path), adapter_mac, device_mac, "Mouse", new_key)
    assert plan2.status == "ALREADY_SYNCED"


def test_plan_device_not_found(tmp_path):
    adapter_name = "4c034fe0d1b0" if os.name == "nt" else "4c:03:4f:e0:d1:b0"
    adapter_dir = tmp_path / adapter_name
    adapter_dir.mkdir(parents=True)

    plan = plan_device_sync(str(tmp_path), "4C:03:4F:E0:D1:B0", "00:11:22:33:44:55", "Missing", "A" * 32)
    assert plan.status == "DEVICE_NOT_FOUND"


def test_generate_updated_info_ble():
    from bt_dualboot.core.registry import BLEData
    lines = SAMPLE_INFO_WITHOUT_LINKKEY.splitlines(keepends=True)
    ble = BLEData(ltk="AABBCCDDEEFF00112233445566778899", ediv=48215, rand=10411030018809425323)
    updated = generate_updated_info(lines, new_key=None, has_link_key_section=False, ble_data=ble)
    text = "".join(updated)
    assert "[LongTermKey]" in text
    assert "Key=AABBCCDDEEFF00112233445566778899" in text
    assert "EDiv=48215" in text
    assert "Rand=10411030018809425323" in text


def test_list_installed_bluez_devices(tmp_path):
    from bt_dualboot.core.bluez import list_installed_bluez_devices
    # Initially empty
    assert list_installed_bluez_devices(str(tmp_path)) == []

    # Create mock adapter and device
    adapter_dir = tmp_path / "4c034fe0d1b0"
    dev_dir = adapter_dir / "54466b0009fb"
    dev_dir.mkdir(parents=True)
    info_file = dev_dir / "info"
    info_file.write_text("[General]\nName=Logitech MX Master 3\n", encoding="utf-8")

    devices = list_installed_bluez_devices(str(tmp_path))
    assert len(devices) == 1
    assert devices[0]["name"] == "Logitech MX Master 3"
    assert devices[0]["device"] == "54466b0009fb"

