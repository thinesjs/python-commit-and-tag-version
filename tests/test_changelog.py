import re
from datetime import date
from pathlib import Path
from unittest.mock import patch

from commit_and_tag_version.defaults import get_default_config
from commit_and_tag_version.lifecycles.changelog import (
    START_OF_LAST_RELEASE_PATTERN,
    changelog,
    generate_changelog_entry,
)
from commit_and_tag_version.models import ParsedCommit


class TestStartOfLastReleasePattern:
    def test_matches_version_heading(self):
        assert re.search(START_OF_LAST_RELEASE_PATTERN, "## [1.0.0]")
        assert re.search(START_OF_LAST_RELEASE_PATTERN, "### [2.3.4]")
        assert re.search(START_OF_LAST_RELEASE_PATTERN, "## 1.0.0")


class TestGenerateChangelogEntry:
    def test_basic_entry(self):
        commits = [
            ParsedCommit(
                type="feat",
                scope=None,
                subject="add feature",
                body=None,
                breaking=False,
                breaking_note=None,
                references=[],
                raw="feat: add feature",
            ),
        ]
        entry = generate_changelog_entry("1.0.0", commits, date=date(2026, 2, 25), tag_prefix="v")
        assert "1.0.0" in entry
        assert "Features" in entry
        assert "add feature" in entry

    def test_groups_by_type(self):
        commits = [
            ParsedCommit(
                type="feat",
                scope=None,
                subject="new thing",
                body=None,
                breaking=False,
                breaking_note=None,
                references=[],
                raw="feat: new thing",
            ),
            ParsedCommit(
                type="fix",
                scope=None,
                subject="fix thing",
                body=None,
                breaking=False,
                breaking_note=None,
                references=[],
                raw="fix: fix thing",
            ),
        ]
        entry = generate_changelog_entry("1.1.0", commits, date=date(2026, 2, 25), tag_prefix="v")
        assert "Features" in entry
        assert "Bug Fixes" in entry

    def test_breaking_changes_section(self):
        commits = [
            ParsedCommit(
                type="feat",
                scope="api",
                subject="changed api",
                body=None,
                breaking=True,
                breaking_note="removed old endpoint",
                references=[],
                raw="feat(api)!: changed api",
            ),
        ]
        entry = generate_changelog_entry("2.0.0", commits, date=date(2026, 2, 25), tag_prefix="v")
        assert "BREAKING CHANGES" in entry

    def test_scoped_commit(self):
        commits = [
            ParsedCommit(
                type="feat",
                scope="cli",
                subject="add option",
                body=None,
                breaking=False,
                breaking_note=None,
                references=[],
                raw="feat(cli): add option",
            ),
        ]
        entry = generate_changelog_entry("1.0.0", commits, date=date(2026, 2, 25), tag_prefix="v")
        assert "**cli:**" in entry

    def test_hidden_types_excluded(self):
        commits = [
            ParsedCommit(
                type="chore",
                scope=None,
                subject="update deps",
                body=None,
                breaking=False,
                breaking_note=None,
                references=[],
                raw="chore: update deps",
            ),
        ]
        entry = generate_changelog_entry("1.0.0", commits, date=date(2026, 2, 25), tag_prefix="v")
        assert "update deps" not in entry


class TestChangelog:
    def test_creates_changelog_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config = get_default_config()
        config.infile = str(tmp_path / "CHANGELOG.md")
        with (
            patch("commit_and_tag_version.lifecycles.changelog.git_log_raw") as mock_log,
            patch("commit_and_tag_version.lifecycles.changelog.get_semver_tags") as mock_tags,
        ):
            mock_log.return_value = ["feat: new feature"]
            mock_tags.return_value = ["1.0.0"]
            changelog(config, "1.0.0")
        assert Path(config.infile).exists()
        content = Path(config.infile).read_text()
        assert "1.0.0" in content

    def test_preserves_existing_content(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        existing = "# Changelog\n\n## [0.1.0] (2026-01-01)\n\n### Features\n\n* old feature\n"
        changelog_path = tmp_path / "CHANGELOG.md"
        changelog_path.write_text(existing)
        config = get_default_config()
        config.infile = str(changelog_path)
        with (
            patch("commit_and_tag_version.lifecycles.changelog.git_log_raw") as mock_log,
            patch("commit_and_tag_version.lifecycles.changelog.get_semver_tags") as mock_tags,
        ):
            mock_log.return_value = ["feat: new feature"]
            mock_tags.return_value = ["0.1.0"]
            changelog(config, "1.0.0")
        content = changelog_path.read_text()
        assert "1.0.0" in content
        assert "0.1.0" in content
