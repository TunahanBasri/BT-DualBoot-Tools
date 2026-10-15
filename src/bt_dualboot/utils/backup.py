"""
Backup and Snapshot Management for Linux BlueZ Configurations.
Enables instant rollback in case of corrupted pairing files or synchronization mistakes.
"""

import os
import shutil
import time
from typing import Optional, List


def create_backup(source_dir: str = "/var/lib/bluetooth", parent_dest: Optional[str] = None) -> Optional[str]:
    """
    Safely creates a timestamped recursive copy of the BlueZ directory.
    Default destination format: /var/lib/bluetooth_backup_<YYYYMMDD_HHMMSS>
    """
    if not os.path.exists(source_dir):
        return None

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    if parent_dest:
        dest_dir = os.path.join(parent_dest, f"bluetooth_backup_{timestamp}")
    else:
        parent = os.path.dirname(os.path.abspath(source_dir))
        dest_dir = os.path.join(parent, f"bluetooth_backup_{timestamp}")

    try:
        shutil.copytree(source_dir, dest_dir, symlinks=True)
        return dest_dir
    except Exception as e:
        print(f"[ERROR] Backup failed: {e}")
        return None


def list_backups(search_dir: str = "/var/lib") -> List[str]:
    """Returns a list of all existing bluetooth backup directories, sorted by newest first."""
    if not os.path.exists(search_dir):
        return []

    backups = []
    try:
        for entry in os.listdir(search_dir):
            if entry.startswith("bluetooth_backup_"):
                full_path = os.path.join(search_dir, entry)
                if os.path.isdir(full_path):
                    backups.append(full_path)
    except PermissionError:
        return []

    backups.sort(reverse=True)
    return backups


def rollback_backup(backup_path: str, target_dir: str = "/var/lib/bluetooth") -> bool:
    """
    Restores the specified backup into the BlueZ configuration directory.
    """
    if not os.path.exists(backup_path):
        print(f"[ERROR] Specified backup path does not exist: {backup_path}")
        return False

    try:
        # If target exists, remove it or clear it
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)

        shutil.copytree(backup_path, target_dir, symlinks=True)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to restore backup: {e}")
        return False
