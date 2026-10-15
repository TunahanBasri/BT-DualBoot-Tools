import os
try:
    import pytest
except ImportError:
    class _RaisesContext:
        def __init__(self, exc): self.exc = exc
        def __enter__(self): return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is None: raise AssertionError(f"Expected {self.exc} not raised")
            return issubclass(exc_type, self.exc)
    class pytest:
        @staticmethod
        def raises(exc): return _RaisesContext(exc)

from bt_dualboot.core.registry import parse_export_json, BluetoothAdapter, PairedDevice


def test_parse_export_json_from_file():
    fixture_path = os.path.join(os.path.dirname(__file__), "fixtures", "mock_btkeys.json")
    adapters = parse_export_json(fixture_path)

    assert len(adapters) == 1
    adapter = adapters[0]
    assert adapter.adapter_mac == "4c:03:4f:e0:d1:b0"
    assert len(adapter.devices) == 2

    dev1 = adapter.devices[0]
    assert dev1.mac == "54:46:6b:00:09:fb"
    assert dev1.name == "Logitech MX Master 3"
    assert dev1.key == "588546EA82C033CE9508E1C74EC74FD6"

    dev2 = adapter.devices[1]
    assert dev2.mac == "f4:4e:fc:21:44:a8"
    assert dev2.name == "Keychron K2 Mechanical Keyboard"


def test_parse_export_json_from_string():
    raw_json = """
    {
        "adapter": "4C:03:4F:E0:D1:B0",
        "devices": [
            {
                "mac": "54:46:6B:00:09:FB",
                "name": "Mouse",
                "key": "588546EA82C033CE9508E1C74EC74FD6"
            }
        ]
    }
    """
    adapters = parse_export_json(raw_json)
    assert len(adapters) == 1
    assert adapters[0].adapter_mac == "4c:03:4f:e0:d1:b0"
    assert len(adapters[0].devices) == 1


def test_parse_invalid_json():
    with pytest.raises(ValueError):
        parse_export_json("NOT_VALID_JSON{")
