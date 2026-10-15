import io
import os
import sys
from contextlib import redirect_stdout
from bt_dualboot.cli import mask_key, Style, main

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
SAMPLE_EXPORT = os.path.join(FIXTURES_DIR, "mock_btkeys.json")


def test_mask_key():
    full_key = "588546EA82C033CE9508E1C74EC74FD6"
    masked = mask_key(full_key, show_full=False)
    assert masked == "5885...4FD6"

    unmasked = mask_key(full_key, show_full=True)
    assert unmasked == full_key

    assert mask_key(None) == ""
    assert mask_key("SHORT") == "SHORT"


def test_style_no_color():
    style_color = Style(disabled=False)
    if not os.environ.get("NO_COLOR"):
        assert "\033[" in style_color.CYAN

    style_no_color = Style(disabled=True)
    assert style_no_color.CYAN == ""
    assert style_no_color.GREEN == ""
    assert style_no_color.RESET == ""


def test_cli_dry_run_with_no_color():
    buf = io.StringIO()
    with redirect_stdout(buf):
        exit_code = main([SAMPLE_EXPORT, "--dry-run", "--no-color", "--bluez-path", FIXTURES_DIR])
    assert exit_code == 0
    output = buf.getvalue()
    assert "\033[" not in output
    assert "SIMULATION MODE" in output
    assert "Synchronization Plan" in output


def test_cli_list_masked_vs_show_keys():
    # Masked by default
    buf1 = io.StringIO()
    with redirect_stdout(buf1):
        code1 = main([SAMPLE_EXPORT, "--list", "--no-color"])
    assert code1 == 0
    out1 = buf1.getvalue()
    assert "5885...4FD6" in out1
    assert "588546EA82C033CE9508E1C74EC74FD6" not in out1

    # Full keys with --show-keys
    buf2 = io.StringIO()
    with redirect_stdout(buf2):
        code2 = main([SAMPLE_EXPORT, "--list", "--show-keys", "--no-color"])
    assert code2 == 0
    out2 = buf2.getvalue()
    assert "588546EA82C033CE9508E1C74EC74FD6" in out2


def test_cli_missing_file_exit_code():
    buf = io.StringIO()
    with redirect_stdout(buf):
        exit_code = main(["non_existent_file.json", "--no-color"])
    assert exit_code == 1
    assert "file not found" in buf.getvalue()
