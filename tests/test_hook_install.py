"""Tests for idempotent rc-file patching, using a throwaway file (never the real rc)."""

from ohnoo.hook.common import BEGIN_MARKER, install_block, uninstall_block


def test_install_is_idempotent(tmp_path):
    rc = tmp_path / "fake_rc"
    rc.write_text("# existing content\n", encoding="utf-8")

    _, installed1 = install_block(rc, "echo hello")
    assert installed1 is True
    assert BEGIN_MARKER in rc.read_text(encoding="utf-8")

    _, installed2 = install_block(rc, "echo hello")
    assert installed2 is False
    # Content should not be duplicated.
    assert rc.read_text(encoding="utf-8").count(BEGIN_MARKER) == 1


def test_install_creates_missing_rc_file(tmp_path):
    rc = tmp_path / "does_not_exist_yet"
    _, installed = install_block(rc, "echo hi")
    assert installed is True
    assert rc.exists()


def test_uninstall_removes_block_and_preserves_other_content(tmp_path):
    rc = tmp_path / "fake_rc"
    rc.write_text("# before\nsome other line\n", encoding="utf-8")
    install_block(rc, "echo hello")

    removed = uninstall_block(rc)
    assert removed is True
    text = rc.read_text(encoding="utf-8")
    assert BEGIN_MARKER not in text
    assert "some other line" in text
    assert "# before" in text


def test_uninstall_on_file_without_block_is_noop(tmp_path):
    rc = tmp_path / "fake_rc"
    rc.write_text("# nothing to see here\n", encoding="utf-8")
    removed = uninstall_block(rc)
    assert removed is False
