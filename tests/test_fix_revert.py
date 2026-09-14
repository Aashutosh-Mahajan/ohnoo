"""Tests for the git-status snapshot + revert safety net around --fix.

Since headless agent CLIs can write files before ohnoo ever shows a diff
(see FixResult's docstring), the best available safety net is: snapshot
git status before running, and offer to revert exactly what changed if the
user doesn't want to keep it.
"""

import subprocess

from ohnoo.agents._common import revert_changes, snapshot_git_status


def _git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


def _init_repo(tmp_path):
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "Test")
    (tmp_path / "tracked.txt").write_text("original\n", encoding="utf-8")
    _git(tmp_path, "add", "tracked.txt")
    _git(tmp_path, "commit", "-q", "-m", "initial")


def test_snapshot_git_status_returns_none_outside_a_repo(tmp_path):
    assert snapshot_git_status(str(tmp_path)) is None


def test_snapshot_git_status_returns_porcelain_output_inside_a_repo(tmp_path):
    _init_repo(tmp_path)
    assert snapshot_git_status(str(tmp_path)) == ""


def test_revert_changes_restores_modified_tracked_file(tmp_path):
    _init_repo(tmp_path)
    before = snapshot_git_status(str(tmp_path))

    (tmp_path / "tracked.txt").write_text("agent modified this\n", encoding="utf-8")
    after = snapshot_git_status(str(tmp_path))

    reverted = revert_changes(str(tmp_path), before, after)

    assert reverted is True
    assert (tmp_path / "tracked.txt").read_text(encoding="utf-8") == "original\n"


def test_revert_changes_deletes_newly_created_untracked_file(tmp_path):
    _init_repo(tmp_path)
    before = snapshot_git_status(str(tmp_path))

    (tmp_path / "new_file.py").write_text("print('hi')\n", encoding="utf-8")
    after = snapshot_git_status(str(tmp_path))

    reverted = revert_changes(str(tmp_path), before, after)

    assert reverted is True
    assert not (tmp_path / "new_file.py").exists()


def test_revert_changes_leaves_pre_existing_untracked_file_alone(tmp_path):
    _init_repo(tmp_path)
    (tmp_path / "already_here.txt").write_text("pre-existing\n", encoding="utf-8")
    before = snapshot_git_status(str(tmp_path))

    (tmp_path / "tracked.txt").write_text("agent modified this\n", encoding="utf-8")
    after = snapshot_git_status(str(tmp_path))

    revert_changes(str(tmp_path), before, after)

    assert (tmp_path / "already_here.txt").exists()


def test_revert_changes_returns_false_when_nothing_changed(tmp_path):
    _init_repo(tmp_path)
    status = snapshot_git_status(str(tmp_path))
    assert revert_changes(str(tmp_path), status, status) is False
