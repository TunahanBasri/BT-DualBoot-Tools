# BT DualBoot Tools - Linux Import (v1.0)

This folder contains scripts to import Classic Bluetooth pairing keys exported from Windows into the Linux BlueZ stack.

## Contents
*   `backup.py`: Backs up `/var/lib/bluetooth` into a timestamped directory (e.g. `/var/lib/bluetooth_backup_YYYYMMDD_HHMMSS`).
*   `import_key.py`: Reads the `btkeys.json` file, triggers `backup.py`, updates BlueZ config files, and restarts the bluetooth service.

## Prerequisites
*   Linux OS with BlueZ (standard Bluetooth stack).
*   Python 3.x.
*   Root privileges (sudo is required to read/write `/var/lib/bluetooth`).
*   **The device must be paired in Linux first.** This generates the adapter and device directories and the default `info` configuration template.

## How it Works
1.  **Backup**: The script runs `backup.py` first to ensure that a copy of your working Bluetooth configs is safely stored in `/var/lib/bluetooth_backup_<timestamp>`.
2.  **Matching**: The script scans `/var/lib/bluetooth` directories, looking for folders corresponding to the adapter and device MAC addresses found in the JSON file. It matches MACs case-insensitively.
3.  **Update**:
    *   **Classic Devices**: Modifies the `Key` value under the `[LinkKey]` section of the `info` configuration file.
4.  **Restart**: Runs `systemctl restart bluetooth` so that BlueZ loads the updated credentials without requiring a reboot.

*Note: Bluetooth Low Energy (LE) keys are not imported in v1.0 and are planned for v1.1.*

## Usage

1.  Copy the `btkeys.json` file (exported from Windows) into this folder (or keep track of its path).
2.  Run the import script using `sudo`:

```bash
# Using the default btkeys.json in the current directory
sudo python import_key.py

# Or specifying the path to the JSON file
sudo python import_key.py /path/to/btkeys.json
```

3.  The Bluetooth service will restart, and your devices should now connect on Linux using the Windows pairing details!
