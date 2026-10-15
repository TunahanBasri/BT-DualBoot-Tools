# Contributing to BT-DualBoot Tools 🤝

Thank you for considering contributing to **BT-DualBoot Tools**! Our goal is to make dual-booting Windows and Linux completely painless for Bluetooth peripherals.

---

## 🛠️ Development Setup

1. **Fork and Clone the Repository:**
   ```bash
   git clone https://github.com/TunahanBasri/bt-dualboot-tools.git
   cd bt-dualboot-tools
   ```

2. **Set up a Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\Activate.ps1
   ```

3. **Install Editable Package with Dev Tools:**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Run the Test Suite:**
   ```bash
   # Using pytest:
   pytest tests -v

   # Or using the built-in standalone runner (zero external dependencies):
   python tests/run_tests.py
   ```

---

## 📋 Code Standards & Guidelines

- **Python**: PEP 8 style guidelines. Type annotations (`typing`) are encouraged.
- **Cross-Platform Compatibility**: BlueZ paths and registry models must be safely mocked so tests can run on any OS (Linux, macOS, Windows).
- **Safety First**: Any modifications to system files must always respect `--dry-run` and provide automatic snapshot backups before applying changes.
- **Zero Sensitive Residuals**: Windows export scripts must always cleanly unregister scheduled tasks and delete temporary registry exports upon completion.

---

## 🚀 Submitting a Pull Request

1. Create a feature branch: `git checkout -b feature/awesome-addition`.
2. Commit your changes: `git commit -m "feat: add support for XYZ"`.
3. Push to your branch: `git push origin feature/awesome-addition`.
4. Open a Pull Request on GitHub describing your motivation and testing verification.
