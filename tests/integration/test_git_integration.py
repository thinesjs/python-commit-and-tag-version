import json
import os
import re
import subprocess
import uuid

import pytest

from commit_and_tag_version import commit_and_tag_version
from commit_and_tag_version.defaults import get_default_config


def _make_commit(repo_path, msg):
    dummy = repo_path / f"dummy-{uuid.uuid4().hex[:8]}.txt"
    dummy.write_text(msg)
    subprocess.run(["git", "add", "."], cwd=repo_path, capture_output=True, check=True)
    subprocess.run(
        ["git", "commit", "-m", msg],
        cwd=repo_path,
        capture_output=True,
        check=True,
    )


def _get_tags(repo_path):
    result = subprocess.run(
        ["git", "tag"], cwd=repo_path, capture_output=True, text=True, check=True
    )
    return [t.strip() for t in result.stdout.strip().split("\n") if t.strip()]


def _get_package_version(repo_path):
    return json.loads((repo_path / "package.json").read_text())["version"]


@pytest.mark.integration
class TestGitIntegration:
    def test_patch_bump(self, git_repo_with_package, monkeypatch):
        monkeypatch.chdir(git_repo_with_package)
        _make_commit(git_repo_with_package, "fix: resolve bug")
        config = get_default_config()
        config.package_files = ["package.json"]
        config.bump_files = ["package.json"]
        commit_and_tag_version(config)
        assert _get_package_version(git_repo_with_package) == "1.0.1"
        assert "v1.0.1" in _get_tags(git_repo_with_package)

    def test_minor_bump(self, git_repo_with_package, monkeypatch):
        monkeypatch.chdir(git_repo_with_package)
        _make_commit(git_repo_with_package, "feat: add new feature")
        config = get_default_config()
        config.package_files = ["package.json"]
        config.bump_files = ["package.json"]
        commit_and_tag_version(config)
        assert _get_package_version(git_repo_with_package) == "1.1.0"
        assert "v1.1.0" in _get_tags(git_repo_with_package)

    def test_major_bump(self, git_repo_with_package, monkeypatch):
        monkeypatch.chdir(git_repo_with_package)
        _make_commit(git_repo_with_package, "feat!: breaking change")
        config = get_default_config()
        config.package_files = ["package.json"]
        config.bump_files = ["package.json"]
        commit_and_tag_version(config)
        assert _get_package_version(git_repo_with_package) == "2.0.0"

    def test_dry_run_no_changes(self, git_repo_with_package, monkeypatch):
        monkeypatch.chdir(git_repo_with_package)
        _make_commit(git_repo_with_package, "feat: new feature")
        config = get_default_config()
        config.package_files = ["package.json"]
        config.bump_files = ["package.json"]
        config.dry_run = True
        commit_and_tag_version(config)
        assert _get_package_version(git_repo_with_package) == "1.0.0"
        assert "v1.1.0" not in _get_tags(git_repo_with_package)

    def test_first_release(self, git_repo, monkeypatch):
        monkeypatch.chdir(git_repo)
        pkg = {"name": "test", "version": "1.0.0"}
        (git_repo / "package.json").write_text(json.dumps(pkg, indent=2) + "\n")
        subprocess.run(["git", "add", "."], cwd=git_repo, capture_output=True, check=True)
        subprocess.run(
            ["git", "commit", "-m", "chore: add package.json"],
            cwd=git_repo,
            capture_output=True,
            check=True,
        )
        _make_commit(git_repo, "feat: initial")
        config = get_default_config()
        config.package_files = ["package.json"]
        config.bump_files = ["package.json"]
        config.first_release = True
        commit_and_tag_version(config)
        assert _get_package_version(git_repo) == "1.0.0"
        assert "v1.0.0" in _get_tags(git_repo)

    def test_changelog_created(self, git_repo_with_package, monkeypatch):
        monkeypatch.chdir(git_repo_with_package)
        _make_commit(git_repo_with_package, "feat: awesome feature")
        config = get_default_config()
        config.package_files = ["package.json"]
        config.bump_files = ["package.json"]
        commit_and_tag_version(config)
        changelog = (git_repo_with_package / "CHANGELOG.md").read_text()
        assert "awesome feature" in changelog

    def test_custom_tag_prefix(self, git_repo_with_package, monkeypatch):
        monkeypatch.chdir(git_repo_with_package)
        subprocess.run(
            ["git", "tag", "-d", "v1.0.0"],
            cwd=git_repo_with_package,
            capture_output=True,
        )
        subprocess.run(
            ["git", "tag", "-a", "release/1.0.0", "-m", "release"],
            cwd=git_repo_with_package,
            capture_output=True,
            check=True,
        )
        _make_commit(git_repo_with_package, "fix: bug")
        config = get_default_config()
        config.package_files = ["package.json"]
        config.bump_files = ["package.json"]
        config.tag_prefix = "release/"
        commit_and_tag_version(config)
        assert "release/1.0.1" in _get_tags(git_repo_with_package)

    def test_release_as(self, git_repo_with_package, monkeypatch):
        monkeypatch.chdir(git_repo_with_package)
        _make_commit(git_repo_with_package, "fix: small fix")
        config = get_default_config()
        config.package_files = ["package.json"]
        config.bump_files = ["package.json"]
        config.release_as = "major"
        commit_and_tag_version(config)
        assert _get_package_version(git_repo_with_package) == "2.0.0"

    def test_dry_run_output_is_parseable_in_non_tty_context(
        self, git_repo_with_package, monkeypatch
    ):
        monkeypatch.chdir(git_repo_with_package)
        _make_commit(git_repo_with_package, "feat: new feature")
        env = {k: v for k, v in os.environ.items() if k not in ("FORCE_COLOR",)}
        env["NO_COLOR"] = "1"
        result = subprocess.run(
            ["commit-and-tag-version", "--dry-run"],
            cwd=git_repo_with_package,
            capture_output=True,
            text=True,
            env=env,
            check=True,
        )
        combined = result.stdout + result.stderr
        assert "\x1b[" not in combined
        match = re.search(r"to ([0-9]+\.[0-9]+\.[0-9]+(?:-[a-zA-Z0-9.]+)?)", combined)
        assert match is not None
        assert match.group(1) == "1.1.0"
