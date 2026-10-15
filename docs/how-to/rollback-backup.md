# How-To: Rollback and Disaster Recovery

Every time `bt-dualboot` modifies `/var/lib/bluetooth`, it automatically captures a timestamped snapshot of the directory before applying changes.

---

## 1. Automatic Snapshot Format

Backups are saved as:
`/var/lib/bluetooth_backup_<YYYYMMDD_HHMMSS>`

Example:
`/var/lib/bluetooth_backup_20261015_013000`

---

## 2. Instant Rollback to Latest Snapshot

If anything goes wrong or you wish to undo a sync, run:

```bash
sudo bt-dualboot --rollback latest
```

This will:
1. Locate the newest `bluetooth_backup_*` directory.
2. Atomically restore it to `/var/lib/bluetooth`.
3. Restart the `bluetooth` systemd daemon.

---

## 3. Rollback to a Specific Historical Snapshot

To restore a specific backup timestamp:

```bash
sudo bt-dualboot --rollback /var/lib/bluetooth_backup_20261015_013000
```

---

## 4. Manual Rollback

If you cannot run the CLI tool, you can manually restore using standard Linux commands:

```bash
sudo systemctl stop bluetooth
sudo rm -rf /var/lib/bluetooth
sudo cp -r /var/lib/bluetooth_backup_20261015_013000 /var/lib/bluetooth
sudo systemctl start bluetooth
```
