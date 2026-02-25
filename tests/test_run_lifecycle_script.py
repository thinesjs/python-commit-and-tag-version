from unittest.mock import MagicMock, patch

from commit_and_tag_version.models import ScriptsConfig
from commit_and_tag_version.run_lifecycle_script import run_lifecycle_script


class TestRunLifecycleScript:
    def test_returns_none_when_no_scripts(self):
        result = run_lifecycle_script(ScriptsConfig(), "prebump", silent=False, dry_run=False)
        assert result is None

    def test_returns_none_when_hook_not_set(self):
        scripts = ScriptsConfig(prebump=None)
        result = run_lifecycle_script(scripts, "prebump", silent=False, dry_run=False)
        assert result is None

    def test_executes_command(self):
        scripts = ScriptsConfig(prebump="echo 1.2.3")
        with patch("commit_and_tag_version.run_lifecycle_script.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="1.2.3\n", stderr="")
            result = run_lifecycle_script(scripts, "prebump", silent=False, dry_run=False)
            assert result == "1.2.3"
            mock_run.assert_called_once()

    def test_dry_run_skips_execution(self):
        scripts = ScriptsConfig(prebump="echo 1.2.3")
        with patch("commit_and_tag_version.run_lifecycle_script.subprocess.run") as mock_run:
            result = run_lifecycle_script(scripts, "prebump", silent=False, dry_run=True)
            mock_run.assert_not_called()
            assert result is None

    def test_returns_stripped_stdout(self):
        scripts = ScriptsConfig(prebump="echo hello")
        with patch("commit_and_tag_version.run_lifecycle_script.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="  hello world  \n", stderr="")
            result = run_lifecycle_script(scripts, "prebump", silent=False, dry_run=False)
            assert result == "hello world"

    def test_returns_none_for_empty_stdout(self):
        scripts = ScriptsConfig(prebump="true")
        with patch("commit_and_tag_version.run_lifecycle_script.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            result = run_lifecycle_script(scripts, "prebump", silent=False, dry_run=False)
            assert result is None

    def test_returns_none_for_none_stdout(self):
        scripts = ScriptsConfig(prebump="true")
        with patch("commit_and_tag_version.run_lifecycle_script.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout=None, stderr="")
            result = run_lifecycle_script(scripts, "prebump", silent=False, dry_run=False)
            assert result is None
