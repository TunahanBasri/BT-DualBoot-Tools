"""
Persona Tests (Foolproof UX & Usability Verification)
Simulates inexperienced/novice personas attempting to sync without proper Windows export,
empty files, manual password attempts, or invalid templates.
"""

import io
import os
import sys
from contextlib import redirect_stdout
from pathlib import Path
from bt_dualboot.cli import main

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
SAMPLE_EXPORT = os.path.join(FIXTURES_DIR, "mock_btkeys.json")

# Import is_valid_btkeys_file, clean_file_path, and interactive_wizard from sync.py
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from sync import is_valid_btkeys_file, clean_file_path, interactive_wizard


def test_novice_persona_missing_file():
    """Persona 1: Novice user runs the tool right after clone without Export-Keys.bat."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        exit_code = main(["non_existent_keys.json", "--no-color"])
    assert exit_code == 1
    out = buf.getvalue()
    assert "file not found" in out
    assert "HENÜZ WINDOWS'TAN 'btkeys.json' ALINMAMIŞ" in out
    assert "Export-Keys.bat" in out
    assert "ELLE YAZILAMAZ" in out


def test_novice_persona_empty_file(tmp_path):
    """Persona 2: User touches an empty btkeys.json (0 bytes) thinking the file just needs to exist."""
    empty_file = tmp_path / "btkeys.json"
    empty_file.write_text("", encoding="utf-8")

    buf = io.StringIO()
    with redirect_stdout(buf):
        exit_code = main([str(empty_file), "--no-color"])
    assert exit_code == 1
    out = buf.getvalue()
    assert "tamamen boş (0 byte)" in out
    assert "HENÜZ WINDOWS'TAN 'btkeys.json' ALINMAMIŞ" in out
    assert "Export-Keys.bat" in out


def test_novice_persona_manual_comment_typist(tmp_path):
    """Persona 3: User opens btkeys.json and tries to manually write '# buraya sifre girin'."""
    comment_file = tmp_path / "btkeys.json"
    comment_file.write_text("# buraya sifre girin\nklavye_sifrem_12345", encoding="utf-8")

    buf = io.StringIO()
    with redirect_stdout(buf):
        exit_code = main([str(comment_file), "--no-color"])
    assert exit_code == 1
    out = buf.getvalue()
    assert "ELLE YAZILAMAZ" in out
    assert "Export-Keys.bat" in out


def test_novice_persona_empty_json_brackets(tmp_path):
    """Persona 4: User creates a dummy JSON with {} or [] without valid devices."""
    dummy_file = tmp_path / "btkeys.json"
    dummy_file.write_text("{}", encoding="utf-8")

    buf = io.StringIO()
    with redirect_stdout(buf):
        exit_code = main([str(dummy_file), "--no-color"])
    assert exit_code == 1
    out = buf.getvalue()
    assert "eşleşmiş geçerli cihaz/anahtar bulunamadı" in out
    assert "Export-Keys.bat" in out


def test_novice_persona_is_valid_helper(tmp_path):
    """Verifies that is_valid_btkeys_file accurately distinguishes invalid files from real exports."""
    # Non existent
    assert is_valid_btkeys_file("non_existent_file.json") is False

    # Empty file
    empty_f = tmp_path / "empty.json"
    empty_f.write_text("", encoding="utf-8")
    assert is_valid_btkeys_file(str(empty_f)) is False

    # Comment text
    comment_f = tmp_path / "comment.json"
    comment_f.write_text("# buraya sifre girin", encoding="utf-8")
    assert is_valid_btkeys_file(str(comment_f)) is False

    # Empty JSON list
    dummy_f = tmp_path / "dummy.json"
    dummy_f.write_text("[]", encoding="utf-8")
    assert is_valid_btkeys_file(str(dummy_f)) is False

    # Real valid sample export
    assert is_valid_btkeys_file(SAMPLE_EXPORT) is True


def test_novice_persona_clean_file_path():
    """Verifies that clean_file_path strips single quotes, double quotes, and PowerShell & prefixes."""
    assert clean_file_path("'C:\\path\\btkeys.json'") == "C:\\path\\btkeys.json"
    assert clean_file_path('"C:\\path with space\\btkeys.json"') == "C:\\path with space\\btkeys.json"
    assert clean_file_path("& 'C:\\path\\btkeys.json' ") == "C:\\path\\btkeys.json"
    assert clean_file_path("  /var/lib/btkeys.json  ") == "/var/lib/btkeys.json"


def test_novice_persona_drag_and_drop_directly_at_menu(tmp_path):
    """Verifies that dragging and dropping a file directly into the main menu prompt works."""
    dummy_file = tmp_path / "btkeys.json"
    dummy_file.write_text("{}", encoding="utf-8")

    old_stdin = sys.stdin
    sys.stdin = io.StringIO(f"'{str(dummy_file)}'\n")
    try:
        buf = io.StringIO()
        with redirect_stdout(buf):
            exit_code = interactive_wizard()
        assert exit_code == 1
        out = buf.getvalue()
        assert "Sürükleyip bıraktığınız dosya algılandı" in out
        assert "eşleşmiş geçerli cihaz/anahtar bulunamadı" in out
    finally:
        sys.stdin = old_stdin
