# ADR 0002: Non-Destructive In-Place INI Stream Parser for BlueZ

* **Status:** Accepted
* **Deciders:** Tunahan Basri, Systems Architecture Team
* **Date:** 2026-10-15

## Context and Problem Statement
Linux BlueZ stores device configuration profiles in `/var/lib/bluetooth/<AdapterMAC>/<DeviceMAC>/info`. Python's standard `configparser` normalizes case, removes comments, and reorders properties, which can cause `bluetoothd` to misinterpret the file or drop user-defined parameters. How should the tool modify only the `[LinkKey]` section without altering any other metadata?

## Considered Options
1. Use standard `configparser.ConfigParser()`.
2. Rewrite the file completely using template strings.
3. Write a custom line-by-line streaming parser that updates only `[LinkKey]` and writes atomically.

## Decision Outcome
Chosen option: **Option 3 (Non-Destructive Streaming Parser + Atomic Write)**.

### Rationale:
- **Preserves Integrity:** All whitespace, comments, casing, and section order remain 100% intact.
- **Atomic File Replacement:** Writes changes to a temporary file (`.info.tmp.<pid>`) and executes an atomic `os.replace` to prevent corrupted configurations in case of power interruption.
- **Tight Scoping:** Modifies or appends only the `Key=` value inside `[LinkKey]`.

## Consequences
* **Positive:** Zero risk of BlueZ configuration corruption.
* **Negative:** Requires custom line parser logic instead of a one-liner library call.
