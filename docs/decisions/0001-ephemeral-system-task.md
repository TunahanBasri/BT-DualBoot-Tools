# ADR 0001: Ephemeral Scheduled Task for Windows SYSTEM Elevation

* **Status:** Accepted
* **Deciders:** Tunahan Basri, Systems Architecture Team
* **Date:** 2026-10-15

## Context and Problem Statement
In Windows, Bluetooth cryptographic pairing keys under `HKLM\SYSTEM\CurrentControlSet\Services\BTHPORT\Parameters\Keys` are guarded by access control lists (ACLs) permitting read access only to the `NT AUTHORITY\SYSTEM` account. Standard Administrator sessions cannot read this registry key directly. How should the tool access these keys safely without introducing security risks or external dependencies?

## Considered Options
1. Require users to download and run Sysinternals `PsExec.exe -s`.
2. Bundle a precompiled C++ rootkit/injection helper binary.
3. Use native Windows Task Scheduler to run an ephemeral task as `NT AUTHORITY\SYSTEM`.
4. Suggest offline registry mounting via Linux (`chntpw`).

## Decision Outcome
Chosen option: **Option 3 (Native Ephemeral Scheduled Task)**.

### Rationale:
- **Zero External Dependencies:** Uses built-in Windows PowerShell cmdlets (`Register-ScheduledTask`, `Start-ScheduledTask`, `Unregister-ScheduledTask`).
- **Antivirus Safe:** Avoids downloading untrusted binaries or trigger flags associated with `psexec`.
- **Zero Residual Footprint:** Cleaned up automatically inside a `try ... finally` block immediately after memory extraction.

## Consequences
* **Positive:** Completely native, transparent PowerShell script requiring zero third-party downloads.
* **Negative:** Requires running the PowerShell session as Administrator to register the scheduled task.
