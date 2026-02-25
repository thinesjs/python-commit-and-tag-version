from unittest.mock import MagicMock, patch

from commit_and_tag_version import commit_and_tag_version
from commit_and_tag_version.defaults import get_default_config


class TestMainOrchestrator:
    def test_full_pipeline(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "package.json").write_text('{"version": "1.0.0"}')
        config = get_default_config()
        config.bump_files = ["package.json"]
        config.package_files = ["package.json"]

        with (
            patch("commit_and_tag_version.lifecycles.bump.git_log_raw") as mock_log,
            patch("commit_and_tag_version.lifecycles.bump.get_semver_tags") as mock_bump_tags,
            patch("commit_and_tag_version.lifecycles.changelog.git_log_raw") as mock_cl_log,
            patch("commit_and_tag_version.lifecycles.changelog.get_semver_tags") as mock_cl_tags,
            patch("commit_and_tag_version.git.subprocess.run") as mock_run,
        ):
            mock_log.return_value = ["feat: new feature"]
            mock_bump_tags.return_value = []
            mock_cl_log.return_value = ["feat: new feature"]
            mock_cl_tags.return_value = ["1.0.0"]
            mock_run.return_value = MagicMock(returncode=0, stdout="main\n", stderr="")
            commit_and_tag_version(config)

    def test_skips_all_stages(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config = get_default_config()
        config.skip.bump = True
        config.skip.changelog = True
        config.skip.commit = True
        config.skip.tag = True
        commit_and_tag_version(config)

    def test_reads_version_from_package_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "package.json").write_text('{"version": "2.5.0"}')
        config = get_default_config()
        config.package_files = ["package.json"]
        config.bump_files = ["package.json"]
        config.skip.changelog = True
        config.skip.commit = True
        config.skip.tag = True

        with (
            patch("commit_and_tag_version.lifecycles.bump.git_log_raw") as mock_log,
            patch("commit_and_tag_version.lifecycles.bump.get_semver_tags") as mock_tags,
        ):
            mock_log.return_value = ["fix: bug"]
            mock_tags.return_value = []
            commit_and_tag_version(config)
        import json

        result = json.loads((tmp_path / "package.json").read_text())
        assert result["version"] == "2.5.1"

    def test_git_tag_fallback(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config = get_default_config()
        config.package_files = ["nonexistent.json"]
        config.bump_files = []
        config.skip.changelog = True
        config.skip.commit = True
        config.skip.tag = True
        config.git_tag_fallback = True

        with (
            patch("commit_and_tag_version.get_latest_semver_tag") as mock_tag,
            patch("commit_and_tag_version.lifecycles.bump.git_log_raw") as mock_log,
            patch("commit_and_tag_version.lifecycles.bump.get_semver_tags"),
        ):
            mock_tag.return_value = "3.0.0"
            mock_log.return_value = ["fix: bug"]
            commit_and_tag_version(config)
