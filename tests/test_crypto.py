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

from bt_dualboot.core.crypto import (
    normalize_mac,
    validate_mac,
    normalize_link_key,
    validate_link_key,
    reverse_endianness_bytes,
    erand_to_bluez_rand,
    ediv_to_int,
)


def test_normalize_mac():
    assert normalize_mac("54466b0009fb") == "54:46:6b:00:09:fb"
    assert normalize_mac("54-46-6B-00-09-FB") == "54:46:6b:00:09:fb"
    assert normalize_mac("54:46:6b:00:09:fb") == "54:46:6b:00:09:fb"

    with pytest.raises(ValueError):
        normalize_mac("INVALID_MAC")


def test_validate_mac():
    assert validate_mac("54:46:6b:00:09:fb") is True
    assert validate_mac("54466b0009fb") is True
    assert validate_mac("short") is False


def test_normalize_link_key():
    raw_key = "58,85,46,ea,82,c0,33,ce,95,08,e1,c7,4e,c7,4f,d6"
    expected = "588546EA82C033CE9508E1C74EC74FD6"
    assert normalize_link_key(raw_key) == expected

    with pytest.raises(ValueError):
        normalize_link_key("TOO_SHORT_KEY")


def test_validate_link_key():
    valid = "588546EA82C033CE9508E1C74EC74FD6"
    assert validate_link_key(valid) is True
    assert validate_link_key("12345") is False


def test_reverse_endianness_bytes():
    assert reverse_endianness_bytes("ABCD") == "CDAB"
    assert reverse_endianness_bytes("11223344") == "44332211"


def test_erand_to_bluez_rand():
    # Little-endian hex input
    erand = "ABCDEF1234567890"
    # Big-endian hex should be 9078563412EFCDAB -> 10410165320322895275 in unsigned 64-bit int
    rand_int = erand_to_bluez_rand(erand)
    assert rand_int == 10410165320322895275


def test_ediv_to_int():
    assert ediv_to_int("0x1234") == 0x1234
    assert ediv_to_int(48215) == 48215
