from unittest.mock import patch

from commit_and_tag_version.defaults import get_default_config
from commit_and_tag_version.lifecycles.tag import tag as tag_lifecycle


class TestTagLifecycle:
    def test_creates_tag_with_prefix(self):
        config = get_default_config()
        with (
            patch("commit_and_tag_version.lifecycles.tag.git_tag") as mock_tag,
            patch("commit_and_tag_version.lifecycles.tag.get_current_branch") as mock_branch,
        ):
            mock_branch.return_value = "main"
            tag_lifecycle("1.0.0", False, config)
            assert mock_tag.call_args[1]["name"] == "v1.0.0"

    def test_custom_prefix(self):
        config = get_default_config()
        config.tag_prefix = "release/"
        with (
            patch("commit_and_tag_version.lifecycles.tag.git_tag") as mock_tag,
            patch("commit_and_tag_version.lifecycles.tag.get_current_branch") as mock_branch,
        ):
            mock_branch.return_value = "main"
            tag_lifecycle("2.0.0", False, config)
            assert mock_tag.call_args[1]["name"] == "release/2.0.0"

    def test_signed_tag(self):
        config = get_default_config()
        config.sign = True
        with (
            patch("commit_and_tag_version.lifecycles.tag.git_tag") as mock_tag,
            patch("commit_and_tag_version.lifecycles.tag.get_current_branch") as mock_branch,
        ):
            mock_branch.return_value = "main"
            tag_lifecycle("1.0.0", False, config)
            assert mock_tag.call_args[1]["sign"] is True

    def test_force_tag(self):
        config = get_default_config()
        config.tag_force = True
        with (
            patch("commit_and_tag_version.lifecycles.tag.git_tag") as mock_tag,
            patch("commit_and_tag_version.lifecycles.tag.get_current_branch") as mock_branch,
        ):
            mock_branch.return_value = "main"
            tag_lifecycle("1.0.0", False, config)
            assert mock_tag.call_args[1]["force"] is True

    def test_skip_tag(self):
        config = get_default_config()
        config.skip.tag = True
        with patch("commit_and_tag_version.lifecycles.tag.git_tag") as mock_tag:
            tag_lifecycle("1.0.0", False, config)
            mock_tag.assert_not_called()

    def test_dry_run(self):
        config = get_default_config()
        config.dry_run = True
        with (
            patch("commit_and_tag_version.lifecycles.tag.git_tag") as mock_tag,
            patch("commit_and_tag_version.lifecycles.tag.get_current_branch") as mock_branch,
        ):
            mock_branch.return_value = "main"
            tag_lifecycle("1.0.0", False, config)
            assert mock_tag.call_args[1]["dry_run"] is True

    def test_publish_hint_no_npm(self, capsys):
        config = get_default_config()
        with (
            patch("commit_and_tag_version.lifecycles.tag.git_tag"),
            patch("commit_and_tag_version.lifecycles.tag.get_current_branch") as mock_branch,
        ):
            mock_branch.return_value = "main"
            tag_lifecycle("1.0.0", False, config)
            captured = capsys.readouterr()
            assert "git push --follow-tags origin main" in captured.err
            assert "npm publish" not in captured.err
