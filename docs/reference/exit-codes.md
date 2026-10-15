# Reference: CLI Exit Codes

Standard exit codes returned by the `bt-dualboot` command-line interface:

| Exit Code | Meaning | Context / Resolution |
| :---: | :--- | :--- |
| **`0`** | **Success** | The operation completed successfully, all devices were already in sync, or dry-run finished cleanly. |
| **`1`** | **Error** | File not found, invalid JSON format, backup restoration failure, or general exception. |
| **`2`** | **Privileges Required** | Sudo / root privileges are required to modify `/var/lib/bluetooth`. Rerun with `sudo bt-dualboot`. |
