from unittest.mock import patch

from commit_and_tag_version.defaults import get_default_config
from commit_and_tag_version.lifecycles.bump import bump


class TestBump:
    def _setup_config(self, tmp_path):
        (tmp_path / "package.json").write_text('{\n  "version": "1.0.0"\n}\n')
        config = get_default_config()
        config.bump_files = ["package.json"]
        config.package_files = ["package.json"]
        return config

    def test_patch_bump_from_fix(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config = self._setup_config(tmp_path)
        with (
            patch("commit_and_tag_version.lifecycles.bump.git_log_raw") as mock_log,
            patch("commit_and_tag_version.lifecycles.bump.get_semver_tags") as mock_tags,
        ):
            mock_log.return_value = ["fix: resolve bug"]
            mock_tags.return_value = []
            assert bump(config, "1.0.0") == "1.0.1"

    def test_minor_bump_from_feat(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config = self._setup_config(tmp_path)
        with (
            patch("commit_and_tag_version.lifecycles.bump.git_log_raw") as mock_log,
            patch("commit_and_tag_version.lifecycles.bump.get_semver_tags") as mock_tags,
        ):
            mock_log.return_value = ["feat: add feature"]
            mock_tags.return_value = []
            assert bump(config, "1.0.0") == "1.1.0"

    def test_major_bump_from_breaking(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config = self._setup_config(tmp_path)
        with (
            patch("commit_and_tag_version.lifecycles.bump.git_log_raw") as mock_log,
            patch("commit_and_tag_version.lifecycles.bump.get_semver_tags") as mock_tags,
        ):
            mock_log.return_value = ["feat!: breaking change"]
            mock_tags.return_value = []
            assert bump(config, "1.0.0") == "2.0.0"

    def test_breaking_before_1_0_0_bumps_minor(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "package.json").write_text('{\n  "version": "0.1.0"\n}\n')
        config = get_default_config()
        config.bump_files = ["package.json"]
        config.package_files = ["package.json"]
        with (
            patch("commit_and_tag_version.lifecycles.bump.git_log_raw") as mock_log,
            patch("commit_and_tag_version.lifecycles.bump.get_semver_tags") as mock_tags,
        ):
            mock_log.return_value = ["feat!: breaking"]
            mock_tags.return_value = []
            assert bump(config, "0.1.0") == "0.2.0"

    def test_release_as_override(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config = self._setup_config(tmp_path)
        config.release_as = "major"
        with (
            patch("commit_and_tag_version.lifecycles.bump.git_log_raw") as mock_log,
            patch("commit_and_tag_version.lifecycles.bump.get_semver_tags") as mock_tags,
        ):
            mock_log.return_value = ["fix: small fix"]
            mock_tags.return_value = []
            assert bump(config, "1.0.0") == "2.0.0"

    def test_release_as_exact_version(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config = self._setup_config(tmp_path)
        config.release_as = "3.0.0"
        with (
            patch("commit_and_tag_version.lifecycles.bump.git_log_raw") as mock_log,
            patch("commit_and_tag_version.lifecycles.bump.get_semver_tags") as mock_tags,
        ):
            mock_log.return_value = []
            mock_tags.return_value = []
            assert bump(config, "1.0.0") == "3.0.0"

    def test_first_release_skips_bump(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config = get_default_config()
        config.first_release = True
        assert bump(config, "1.0.0") == "1.0.0"

    def test_prerelease_basic(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config = self._setup_config(tmp_path)
        config.prerelease = "alpha"
        with (
            patch("commit_and_tag_version.lifecycles.bump.git_log_raw") as mock_log,
            patch("commit_and_tag_version.lifecycles.bump.get_semver_tags") as mock_tags,
        ):
            mock_log.return_value = ["feat: feature"]
            mock_tags.return_value = []
            assert bump(config, "1.0.0") == "1.1.0-alpha.0"

    def test_release_as_major_with_prerelease_from_clean(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config = self._setup_config(tmp_path)
        config.release_as = "major"
        config.prerelease = "rc"
        with (
            patch("commit_and_tag_version.lifecycles.bump.git_log_raw") as mock_log,
            patch("commit_and_tag_version.lifecycles.bump.get_semver_tags") as mock_tags,
        ):
            mock_log.return_value = []
            mock_tags.return_value = []
            assert bump(config, "1.0.0") == "2.0.0-rc.0"

    def test_release_as_major_with_prerelease_from_existing_prerelease(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config = self._setup_config(tmp_path)
        config.release_as = "major"
        config.prerelease = "rc"
        with (
            patch("commit_and_tag_version.lifecycles.bump.git_log_raw") as mock_log,
            patch("commit_and_tag_version.lifecycles.bump.get_semver_tags") as mock_tags,
        ):
            mock_log.return_value = []
            mock_tags.return_value = []
            assert bump(config, "0.0.1-rc.15") == "1.0.0-rc.0"

    def test_release_as_minor_with_prerelease_from_existing_prerelease(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config = self._setup_config(tmp_path)
        config.release_as = "minor"
        config.prerelease = "rc"
        with (
            patch("commit_and_tag_version.lifecycles.bump.git_log_raw") as mock_log,
            patch("commit_and_tag_version.lifecycles.bump.get_semver_tags") as mock_tags,
        ):
            mock_log.return_value = []
            mock_tags.return_value = []
            assert bump(config, "0.0.1-rc.15") == "0.1.0-rc.0"

    def test_release_as_lower_priority_continues_prerelease(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config = self._setup_config(tmp_path)
        config.release_as = "patch"
        config.prerelease = "rc"
        with (
            patch("commit_and_tag_version.lifecycles.bump.git_log_raw") as mock_log,
            patch("commit_and_tag_version.lifecycles.bump.get_semver_tags") as mock_tags,
        ):
            mock_log.return_value = []
            mock_tags.return_value = []
            assert bump(config, "1.0.0-rc.0") == "1.0.0-rc.1"

    def test_auto_continue_prerelease_when_active_type_matches(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config = self._setup_config(tmp_path)
        config.prerelease = "rc"
        with (
            patch("commit_and_tag_version.lifecycles.bump.git_log_raw") as mock_log,
            patch("commit_and_tag_version.lifecycles.bump.get_semver_tags") as mock_tags,
        ):
            mock_log.return_value = ["feat!: breaking"]
            mock_tags.return_value = []
            assert bump(config, "1.0.0-rc.0") == "1.0.0-rc.1"

    def test_auto_continue_prerelease_when_active_type_higher_priority(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config = self._setup_config(tmp_path)
        config.prerelease = "rc"
        with (
            patch("commit_and_tag_version.lifecycles.bump.git_log_raw") as mock_log,
            patch("commit_and_tag_version.lifecycles.bump.get_semver_tags") as mock_tags,
        ):
            mock_log.return_value = ["fix: small"]
            mock_tags.return_value = []
            assert bump(config, "1.0.0-rc.0") == "1.0.0-rc.1"

    def test_auto_escalates_prerelease_when_recommended_type_higher(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config = self._setup_config(tmp_path)
        config.prerelease = "rc"
        with (
            patch("commit_and_tag_version.lifecycles.bump.git_log_raw") as mock_log,
            patch("commit_and_tag_version.lifecycles.bump.get_semver_tags") as mock_tags,
        ):
            mock_log.return_value = ["feat!: breaking"]
            mock_tags.return_value = []
            assert bump(config, "1.2.0-rc.0") == "2.0.0-rc.0"

    def test_updates_bump_files(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config = self._setup_config(tmp_path)
        with (
            patch("commit_and_tag_version.lifecycles.bump.git_log_raw") as mock_log,
            patch("commit_and_tag_version.lifecycles.bump.get_semver_tags") as mock_tags,
        ):
            mock_log.return_value = ["fix: bug"]
            mock_tags.return_value = []
            bump(config, "1.0.0")
        import json

        updated = json.loads((tmp_path / "package.json").read_text())
        assert updated["version"] == "1.0.1"

    def test_prebump_hook_overrides_version(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config = self._setup_config(tmp_path)
        config.scripts.prebump = "echo 5.0.0"
        with (
            patch("commit_and_tag_version.lifecycles.bump.run_lifecycle_script") as mock_script,
            patch("commit_and_tag_version.lifecycles.bump.git_log_raw"),
            patch("commit_and_tag_version.lifecycles.bump.get_semver_tags") as mock_tags,
        ):
            mock_script.side_effect = [None, "5.0.0", None]
            mock_tags.return_value = []
            result = bump(config, "1.0.0")
            assert result == "5.0.0"

    def test_prebump_hook_invalid_version_ignored(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config = self._setup_config(tmp_path)
        config.scripts.prebump = "echo not-a-version"
        with (
            patch("commit_and_tag_version.lifecycles.bump.run_lifecycle_script") as mock_script,
            patch("commit_and_tag_version.lifecycles.bump.git_log_raw") as mock_log,
            patch("commit_and_tag_version.lifecycles.bump.get_semver_tags") as mock_tags,
        ):
            mock_script.side_effect = [None, "not-a-version", None]
            mock_log.return_value = ["fix: bug"]
            mock_tags.return_value = []
            result = bump(config, "1.0.0")
            assert result == "1.0.1"

    def test_prebump_hook_none_continues_normally(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config = self._setup_config(tmp_path)
        with (
            patch("commit_and_tag_version.lifecycles.bump.git_log_raw") as mock_log,
            patch("commit_and_tag_version.lifecycles.bump.get_semver_tags") as mock_tags,
        ):
            mock_log.return_value = ["feat: new thing"]
            mock_tags.return_value = []
            result = bump(config, "1.0.0")
            assert result == "1.1.0"
