# How-To: Synchronize Bluetooth Devices

This guide covers advanced device synchronization scenarios using `bt-dualboot`.

---

## 1. Inspecting Exported Keys Without Applying

To inspect the contents of an exported `btkeys.json` file without touching any system configurations:

```bash
# Display devices with masked keys for shoulder-surfing protection
python -m bt_dualboot.cli btkeys.json --list

# Display full unmasked 128-bit hexadecimal keys
python -m bt_dualboot.cli btkeys.json --list --show-keys
```

---

## 2. Using Simulation Mode (`--dry-run`)

Always preview proposed modifications before committing changes to `/var/lib/bluetooth`:

```bash
python -m bt_dualboot.cli btkeys.json --dry-run
```

Expected output:
```text
Synchronization Plan:
Device Name              Device MAC         Status             Details
---------------------------------------------------------------------------
Logitech MX Master 3     54:46:6b:00:09:fb  WILL UPDATE        Key: 1111...1111 -> 5885...4FD6
Keychron K2 Mechanical   f4:4e:fc:21:44:a8  IN SYNC            Pairing keys already match.
---------------------------------------------------------------------------
Summary: 1 already synced, 1 to update, 0 not found in Linux
```

---

## 3. Custom BlueZ Directory

If you store BlueZ data in a non-standard location or are testing within a chroot/container:

```bash
sudo bt-dualboot btkeys.json --bluez-path /mnt/custom/bluetooth
```

---

## 4. Automation and CI Environments

To run in automated scripts without color codes and without restarting the daemon:

```bash
sudo bt-dualboot btkeys.json --no-color --no-restart
```
