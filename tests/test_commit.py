from unittest.mock import patch

from commit_and_tag_version.defaults import get_default_config
from commit_and_tag_version.lifecycles.commit import commit as commit_lifecycle


class TestCommitLifecycle:
    def test_stages_changelog_and_bump_files(self):
        config = get_default_config()
        with (
            patch("commit_and_tag_version.lifecycles.commit.git_add") as mock_add,
            patch("commit_and_tag_version.lifecycles.commit.git_commit"),
            patch("commit_and_tag_version.lifecycles.commit.get_updated_configs") as mock_configs,
        ):
            mock_configs.return_value = {"package.json": True}
            commit_lifecycle(config, "1.0.1")
            add_files = mock_add.call_args[0][0]
            assert "CHANGELOG.md" in add_files
            assert "package.json" in add_files

    def test_commit_message_contains_version(self):
        config = get_default_config()
        with (
            patch("commit_and_tag_version.lifecycles.commit.git_add"),
            patch("commit_and_tag_version.lifecycles.commit.git_commit") as mock_commit,
            patch("commit_and_tag_version.lifecycles.commit.get_updated_configs") as mock_configs,
        ):
            mock_configs.return_value = {}
            commit_lifecycle(config, "2.0.0")
            msg = mock_commit.call_args[1].get(
                "message", mock_commit.call_args[0][0] if mock_commit.call_args[0] else ""
            )
            assert "2.0.0" in msg

    def test_sign_flag(self):
        config = get_default_config()
        config.sign = True
        with (
            patch("commit_and_tag_version.lifecycles.commit.git_add"),
            patch("commit_and_tag_version.lifecycles.commit.git_commit") as mock_commit,
            patch("commit_and_tag_version.lifecycles.commit.get_updated_configs") as mock_configs,
        ):
            mock_configs.return_value = {}
            commit_lifecycle(config, "1.0.0")
            assert mock_commit.call_args[1].get("sign") is True

    def test_no_verify_flag(self):
        config = get_default_config()
        config.no_verify = True
        with (
            patch("commit_and_tag_version.lifecycles.commit.git_add"),
            patch("commit_and_tag_version.lifecycles.commit.git_commit") as mock_commit,
            patch("commit_and_tag_version.lifecycles.commit.get_updated_configs") as mock_configs,
        ):
            mock_configs.return_value = {}
            commit_lifecycle(config, "1.0.0")
            assert mock_commit.call_args[1].get("no_verify") is True

    def test_skip_commit(self):
        config = get_default_config()
        config.skip.commit = True
        with patch("commit_and_tag_version.lifecycles.commit.git_add") as mock_add:
            commit_lifecycle(config, "1.0.0")
            mock_add.assert_not_called()

    def test_dry_run(self):
        config = get_default_config()
        config.dry_run = True
        with (
            patch("commit_and_tag_version.lifecycles.commit.git_add") as mock_add,
            patch("commit_and_tag_version.lifecycles.commit.git_commit"),
            patch("commit_and_tag_version.lifecycles.commit.get_updated_configs") as mock_configs,
        ):
            mock_configs.return_value = {}
            commit_lifecycle(config, "1.0.0")
            assert mock_add.call_args[1].get("dry_run") is True

    def test_commit_all_always_adds_specific_files(self):
        config = get_default_config()
        config.commit_all = True
        with (
            patch("commit_and_tag_version.lifecycles.commit.git_add") as mock_add,
            patch("commit_and_tag_version.lifecycles.commit.git_commit"),
            patch("commit_and_tag_version.lifecycles.commit.get_updated_configs") as mock_configs,
        ):
            mock_configs.return_value = {"package.json": True}
            commit_lifecycle(config, "1.0.0")
            add_files = mock_add.call_args[0][0]
            assert "CHANGELOG.md" in add_files
            assert "package.json" in add_files
            assert "-A" not in add_files

    def test_commit_all_omits_files_from_git_commit(self):
        config = get_default_config()
        config.commit_all = True
        with (
            patch("commit_and_tag_version.lifecycles.commit.git_add"),
            patch("commit_and_tag_version.lifecycles.commit.git_commit") as mock_commit,
            patch("commit_and_tag_version.lifecycles.commit.get_updated_configs") as mock_configs,
        ):
            mock_configs.return_value = {}
            commit_lifecycle(config, "1.0.0")
            assert mock_commit.call_args[1].get("files") is None

    def test_commit_not_all_passes_files_to_git_commit(self):
        config = get_default_config()
        config.commit_all = False
        with (
            patch("commit_and_tag_version.lifecycles.commit.git_add"),
            patch("commit_and_tag_version.lifecycles.commit.git_commit") as mock_commit,
            patch("commit_and_tag_version.lifecycles.commit.get_updated_configs") as mock_configs,
        ):
            mock_configs.return_value = {"package.json": True}
            commit_lifecycle(config, "1.0.0")
            files = mock_commit.call_args[1].get("files")
            assert files is not None
            assert "CHANGELOG.md" in files
            assert "package.json" in files

    def test_precommit_hook_overrides_commit_message(self):
        config = get_default_config()
        config.scripts.precommit = "echo 'custom: release {{currentTag}}'"
        with (
            patch("commit_and_tag_version.lifecycles.commit.git_add"),
            patch("commit_and_tag_version.lifecycles.commit.git_commit") as mock_commit,
            patch("commit_and_tag_version.lifecycles.commit.get_updated_configs") as mock_configs,
            patch("commit_and_tag_version.lifecycles.commit.run_lifecycle_script") as mock_script,
        ):
            mock_script.side_effect = [
                "custom: release {{currentTag}}",
                None,
            ]
            mock_configs.return_value = {}
            commit_lifecycle(config, "3.0.0")
            msg = mock_commit.call_args[1].get("message")
            assert "custom: release 3.0.0" in msg

    def test_precommit_hook_none_keeps_default_message(self):
        config = get_default_config()
        with (
            patch("commit_and_tag_version.lifecycles.commit.git_add"),
            patch("commit_and_tag_version.lifecycles.commit.git_commit") as mock_commit,
            patch("commit_and_tag_version.lifecycles.commit.get_updated_configs") as mock_configs,
            patch("commit_and_tag_version.lifecycles.commit.run_lifecycle_script") as mock_script,
        ):
            mock_script.return_value = None
            mock_configs.return_value = {}
            commit_lifecycle(config, "1.0.0")
            msg = mock_commit.call_args[1].get("message")
            assert "1.0.0" in msg
