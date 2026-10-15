"""
Test runner script.
Executes test functions across tests/ folder using standard Python.
Can also be run via: pytest
"""

import os
import sys
import inspect
import tempfile
from pathlib import Path

# Add src and tests to python path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import test_crypto
import test_registry
import test_bluez
import test_backup
import test_cli
import test_personas


class TmpPathWrapper:
    """Provides pytest-like tmp_path functionality using tempfile."""

    def __init__(self):
        self._temp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self._temp_dir.name)

    def __enter__(self):
        return self.path

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._temp_dir.cleanup()


def run_module_tests(module):
    test_funcs = [
        obj
        for name, obj in inspect.getmembers(module)
        if inspect.isfunction(obj) and name.startswith("test_")
    ]

    passed = 0
    failed = 0

    print(f"\nRunning tests in {module.__name__} ({len(test_funcs)} tests):")
    for func in test_funcs:
        sig = inspect.signature(func)
        try:
            if "tmp_path" in sig.parameters:
                with TmpPathWrapper() as tmp_path:
                    func(tmp_path)
            else:
                func()
            print(f"  [PASS] {func.__name__}")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {func.__name__}: {e}")
            failed += 1

    return passed, failed


def main():
    modules = [test_crypto, test_registry, test_bluez, test_backup, test_cli, test_personas]
    total_passed = 0
    total_failed = 0

    print("========================================")
    print("      BT-DualBoot Tools Test Runner     ")
    print("========================================")

    for mod in modules:
        p, f = run_module_tests(mod)
        total_passed += p
        total_failed += f

    print("\n----------------------------------------")
    print(f"Total: {total_passed + total_failed} | Passed: {total_passed} | Failed: {total_failed}")
    print("----------------------------------------")

    if total_failed > 0:
        sys.exit(1)
    else:
        print("ALL TESTS PASSED SUCCESSFULLY!\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
