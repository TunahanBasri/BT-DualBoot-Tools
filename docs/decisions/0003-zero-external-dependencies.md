# ADR 0003: Zero External Dependencies Policy

* **Status:** Accepted
* **Deciders:** Tunahan Basri, Systems Architecture Team
* **Date:** 2026-10-15

## Context and Problem Statement
When a user boots into a fresh Linux installation or recovery environment without internet connectivity, external Python dependencies (such as `click`, `rich`, `pydantic`, or `typer`) may not be installed. Forcing the user to run `pip install` before their Bluetooth mouse or keyboard functions creates a frustrating chicken-and-egg problem.

## Considered Options
1. Use high-level modern CLI libraries (`click`, `rich`, `typer`).
2. Require third-party native libraries (`pywin32`, `hivex`).
3. Commit to zero external runtime dependencies (`dependencies = []`), using only standard library modules (`argparse`, `dataclasses`, `re`, `shutil`, `tempfile`).

## Decision Outcome
Chosen option: **Option 3 (Zero External Runtime Dependencies)**.

### Rationale:
- **Immediate Execution:** Works out-of-the-box on every standard Python 3.8+ environment.
- **Offline Reliability:** Users can sync their peripherals without an active internet connection.
- **Minimal Attack Surface:** Eliminates supply chain risks (CVEs in third-party packages).

## Consequences
* **Positive:** Flawless portability across Fedora, Ubuntu, Arch, Debian, openSUSE, and Alpine.
* **Negative:** Terminal formatting (colors, tables, padding) must be handled using native ANSI helpers.
