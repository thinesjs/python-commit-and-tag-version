import json

from commit_and_tag_version.config import load_config
from commit_and_tag_version.models import Config


class TestLoadConfig:
    def test_returns_config_with_defaults(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config = load_config({})
        assert isinstance(config, Config)
        assert config.tag_prefix == "v"
        assert config.infile == "CHANGELOG.md"

    def test_cli_args_override_defaults(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config = load_config({"tag_prefix": "release-"})
        assert config.tag_prefix == "release-"

    def test_loads_versionrc_json(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        rc = {"tagPrefix": "release/", "releaseCount": 0}
        (tmp_path / ".versionrc.json").write_text(json.dumps(rc))
        config = load_config({})
        assert config.tag_prefix == "release/"
        assert config.release_count == 0

    def test_loads_versionrc(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        rc = {"tagPrefix": "rc-"}
        (tmp_path / ".versionrc").write_text(json.dumps(rc))
        config = load_config({})
        assert config.tag_prefix == "rc-"

    def test_loads_pyproject_toml(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        toml_content = '[tool.commit-and-tag-version]\ntagPrefix = "pkg-"\n'
        (tmp_path / "pyproject.toml").write_text(toml_content)
        config = load_config({})
        assert config.tag_prefix == "pkg-"

    def test_cli_overrides_file_config(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        rc = {"tagPrefix": "file-"}
        (tmp_path / ".versionrc.json").write_text(json.dumps(rc))
        config = load_config({"tag_prefix": "cli-"})
        assert config.tag_prefix == "cli-"

    def test_versionrc_takes_precedence_over_pyproject(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        rc = {"tagPrefix": "rc-"}
        (tmp_path / ".versionrc.json").write_text(json.dumps(rc))
        toml_content = '[tool.commit-and-tag-version]\ntagPrefix = "pyproject-"\n'
        (tmp_path / "pyproject.toml").write_text(toml_content)
        config = load_config({})
        assert config.tag_prefix == "rc-"

    def test_custom_config_path(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        custom = tmp_path / "custom.json"
        custom.write_text(json.dumps({"tagPrefix": "custom-"}))
        config = load_config({"config": str(custom)})
        assert config.tag_prefix == "custom-"

    def test_skip_config_from_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        rc = {"skip": {"changelog": True}}
        (tmp_path / ".versionrc.json").write_text(json.dumps(rc))
        config = load_config({})
        assert config.skip.changelog is True
        assert config.skip.bump is False

    def test_scripts_config_from_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        rc = {"scripts": {"prebump": "echo 1.0.0"}}
        (tmp_path / ".versionrc.json").write_text(json.dumps(rc))
        config = load_config({})
        assert config.scripts.prebump == "echo 1.0.0"
