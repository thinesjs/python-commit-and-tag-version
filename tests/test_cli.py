from unittest.mock import patch

from click.testing import CliRunner

from commit_and_tag_version.cli import main


class TestCLI:
    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "commit-and-tag-version" in result.output or "Usage" in result.output

    def test_dry_run_option(self):
        runner = CliRunner()
        with patch("commit_and_tag_version.cli.commit_and_tag_version") as mock_catv:
            runner.invoke(main, ["--dry-run"], catch_exceptions=False)
            mock_catv.assert_called_once()
            config = mock_catv.call_args[0][0]
            assert config.dry_run is True

    def test_tag_prefix_option(self):
        runner = CliRunner()
        with patch("commit_and_tag_version.cli.commit_and_tag_version") as mock_catv:
            runner.invoke(main, ["--tag-prefix", "release/"], catch_exceptions=False)
            mock_catv.assert_called_once()
            config = mock_catv.call_args[0][0]
            assert config.tag_prefix == "release/"

    def test_first_release_flag(self):
        runner = CliRunner()
        with patch("commit_and_tag_version.cli.commit_and_tag_version") as mock_catv:
            runner.invoke(main, ["--first-release"], catch_exceptions=False)
            mock_catv.assert_called_once()
            config = mock_catv.call_args[0][0]
            assert config.first_release is True

    def test_release_as_option(self):
        runner = CliRunner()
        with patch("commit_and_tag_version.cli.commit_and_tag_version") as mock_catv:
            runner.invoke(main, ["--release-as", "minor"], catch_exceptions=False)
            mock_catv.assert_called_once()
            config = mock_catv.call_args[0][0]
            assert config.release_as == "minor"

    def test_skip_bump_flag(self):
        runner = CliRunner()
        with patch("commit_and_tag_version.cli.commit_and_tag_version") as mock_catv:
            runner.invoke(main, ["--skip-bump"], catch_exceptions=False)
            mock_catv.assert_called_once()
            config = mock_catv.call_args[0][0]
            assert config.skip.bump is True

    def test_skip_changelog_flag(self):
        runner = CliRunner()
        with patch("commit_and_tag_version.cli.commit_and_tag_version") as mock_catv:
            runner.invoke(main, ["--skip-changelog"], catch_exceptions=False)
            mock_catv.assert_called_once()
            config = mock_catv.call_args[0][0]
            assert config.skip.changelog is True

    def test_skip_commit_flag(self):
        runner = CliRunner()
        with patch("commit_and_tag_version.cli.commit_and_tag_version") as mock_catv:
            runner.invoke(main, ["--skip-commit"], catch_exceptions=False)
            mock_catv.assert_called_once()
            config = mock_catv.call_args[0][0]
            assert config.skip.commit is True

    def test_skip_tag_flag(self):
        runner = CliRunner()
        with patch("commit_and_tag_version.cli.commit_and_tag_version") as mock_catv:
            runner.invoke(main, ["--skip-tag"], catch_exceptions=False)
            mock_catv.assert_called_once()
            config = mock_catv.call_args[0][0]
            assert config.skip.tag is True

    def test_multiple_skip_flags(self):
        runner = CliRunner()
        with patch("commit_and_tag_version.cli.commit_and_tag_version") as mock_catv:
            runner.invoke(main, ["--skip-bump", "--skip-tag"], catch_exceptions=False)
            mock_catv.assert_called_once()
            config = mock_catv.call_args[0][0]
            assert config.skip.bump is True
            assert config.skip.tag is True
            assert config.skip.changelog is False
            assert config.skip.commit is False
