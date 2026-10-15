# Reference: CLI Options & Flags

Complete reference for command-line arguments supported by `bt-dualboot`.

---

## Command Syntax

```bash
bt-dualboot [json_path] [OPTIONS]
```

Or when running from source:
```bash
python -m bt_dualboot.cli [json_path] [OPTIONS]
```

---

## Positional Arguments

| Argument | Default | Description |
| :--- | :--- | :--- |
| `json_path` | `btkeys.json` | Path to the exported JSON file containing paired device keys. |

---

## Options & Flags

| Flag | Description |
| :--- | :--- |
| `--dry-run` | Run the sync in simulation mode. Does not touch or modify any system files. |
| `--bluez-path <PATH>` | Custom directory for BlueZ storage (default: `/var/lib/bluetooth`). |
| `--no-backup` | Skip automated snapshot backup of `/var/lib/bluetooth` before applying updates. |
| `--no-restart` | Do not restart the `bluetooth` systemd daemon after writing changes. |
| `--list` | Display all adapters and devices contained in the export JSON file and exit. |
| `--show-keys` | Display full unmasked 128-bit cryptographic LinkKeys in terminal output. |
| `--no-color` | Disable ANSI color sequences in stdout (supports NO_COLOR standard). |
| `--rollback [PATH\|latest]` | Restore a previous BlueZ configuration snapshot (`latest` or specific path). |
| `-v, --version` | Show program's version number and exit. |
| `-h, --help` | Show help message and exit. |
