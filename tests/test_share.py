"""Tests for --share PNG roast card rendering."""

from ohnoo.engine import Diagnosis
from ohnoo.share import render_share_card


def _diagnosis() -> Diagnosis:
    return Diagnosis(
        matched=True,
        joke="'requests' does not exist in this timeline. Try pip install.",
        fix_summary="Install the missing package.",
        fix_command="pip install requests",
        pattern_id="py-module-not-found",
    )


def test_render_share_card_writes_png_to_given_path(tmp_path):
    output = tmp_path / "card.png"
    result = render_share_card(_diagnosis(), command="python app.py", output_path=output)

    assert result == output
    assert result.exists()
    assert result.stat().st_size > 1000


def test_render_share_card_default_output_path_uses_home_cache(tmp_path, monkeypatch):
    # Point HOME at a tmp dir so we never touch the real user's ~/.cache.
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))

    result = render_share_card(_diagnosis())

    assert result.exists()
    assert result.stat().st_size > 1000
    assert str(tmp_path) in str(result)
    assert result.parent.name == "shares"


def test_render_share_card_without_command_still_renders(tmp_path):
    output = tmp_path / "no_command.png"
    diagnosis = Diagnosis(
        matched=True,
        joke="Nothing is listening on localhost:5432. Did you forget to start it?",
        fix_summary="Start the service.",
        fix_command="",
        pattern_id="node-econnrefused",
    )

    result = render_share_card(diagnosis, output_path=output)

    assert result.exists()
    assert result.stat().st_size > 1000
