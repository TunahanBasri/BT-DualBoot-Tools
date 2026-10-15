import os
import shutil
try:
    import pytest
except ImportError:
    pytest = None
from bt_dualboot.utils.backup import create_backup, list_backups, rollback_backup


def test_backup_and_rollback_cycle(tmp_path):
    source_dir = tmp_path / "bluetooth"
    source_dir.mkdir()
    sample_file = source_dir / "sample.conf"
    sample_file.write_text("initial_state", encoding="utf-8")

    # 1. Create backup in parent folder
    backup_path = create_backup(str(source_dir), parent_dest=str(tmp_path))
    assert backup_path is not None
    assert os.path.exists(backup_path)

    # 2. Modify original file
    sample_file.write_text("corrupted_state", encoding="utf-8")
    assert sample_file.read_text(encoding="utf-8") == "corrupted_state"

    # 3. List backups
    found = list_backups(str(tmp_path))
    assert len(found) >= 1
    assert found[0] == backup_path

    # 4. Rollback
    success = rollback_backup(backup_path, str(source_dir))
    assert success is True
    assert sample_file.read_text(encoding="utf-8") == "initial_state"
