# backup.py
# Part of BT DualBoot Tools
#
# Description: Safely backs up the Linux BlueZ configuration directory (/var/lib/bluetooth).
#
# Requirements: Must be run as root (sudo).

import os
import shutil
import sys
import time

def check_root():
    if os.name == 'nt':
        print("[ERROR] Backup script is designed for Linux only.")
        sys.exit(1)
    if os.geteuid() != 0:
        print("[ERROR] This script must be run as root (sudo).")
        sys.exit(1)

def create_backup(source_dir='/var/lib/bluetooth'):
    if not os.path.exists(source_dir):
        print(f"[ERROR] BlueZ directory not found at: {source_dir}")
        return None

    # Generate a timestamped backup directory name
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    backup_dest = f"/var/lib/bluetooth_backup_{timestamp}"

    print(f"[*] Backing up {source_dir} to {backup_dest}...")
    try:
        # Copy directory structure and permissions
        shutil.copytree(source_dir, backup_dest, symlinks=True)
        print(f"[SUCCESS] Backup successfully created at: {backup_dest}")
        return backup_dest
    except Exception as e:
        print(f"[ERROR] Failed to back up bluetooth configurations: {e}")
        return None

if __name__ == "__main__":
    check_root()
    dest = create_backup()
    if not dest:
        sys.exit(1)
