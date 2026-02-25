from unittest.mock import MagicMock, patch

from commit_and_tag_version.git import (
    get_latest_semver_tag,
    get_semver_tags,
    git_add,
    git_commit,
    git_log_raw,
    git_tag,
)


class TestGitAdd:
    def test_calls_git_add_with_files(self):
        with patch("commit_and_tag_version.git.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            git_add(["file1.txt", "file2.txt"])
            cmd = mock_run.call_args[0][0]
            assert cmd == ["git", "add", "file1.txt", "file2.txt"]

    def test_dry_run_skips_execution(self):
        with patch("commit_and_tag_version.git.subprocess.run") as mock_run:
            git_add(["file1.txt"], dry_run=True)
            mock_run.assert_not_called()


class TestGitCommit:
    def test_basic_commit(self):
        with patch("commit_and_tag_version.git.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            git_commit("test message")
            cmd = mock_run.call_args[0][0]
            assert "commit" in cmd
            assert "-m" in cmd
            assert "test message" in cmd

    def test_sign_flag(self):
        with patch("commit_and_tag_version.git.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            git_commit("msg", sign=True)
            cmd = mock_run.call_args[0][0]
            assert "--gpg-sign" in cmd

    def test_signoff_flag(self):
        with patch("commit_and_tag_version.git.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            git_commit("msg", signoff=True)
            cmd = mock_run.call_args[0][0]
            assert "--signoff" in cmd

    def test_no_verify_flag(self):
        with patch("commit_and_tag_version.git.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            git_commit("msg", no_verify=True)
            cmd = mock_run.call_args[0][0]
            assert "--no-verify" in cmd

    def test_files_appended_after_message(self):
        with patch("commit_and_tag_version.git.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            git_commit("msg", files=["CHANGELOG.md", "package.json"])
            cmd = mock_run.call_args[0][0]
            m_idx = cmd.index("-m")
            msg_idx = cmd.index("msg")
            cl_idx = cmd.index("CHANGELOG.md")
            pkg_idx = cmd.index("package.json")
            assert m_idx < msg_idx < cl_idx < pkg_idx

    def test_no_files_when_none(self):
        with patch("commit_and_tag_version.git.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            git_commit("msg", files=None)
            cmd = mock_run.call_args[0][0]
            assert cmd == ["git", "commit", "-m", "msg"]


class TestGitTag:
    def test_annotated_tag(self):
        with patch("commit_and_tag_version.git.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            git_tag("v1.0.0", "release 1.0.0")
            cmd = mock_run.call_args[0][0]
            assert "tag" in cmd
            assert "-a" in cmd
            assert "v1.0.0" in cmd

    def test_signed_tag(self):
        with patch("commit_and_tag_version.git.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            git_tag("v1.0.0", "release", sign=True)
            cmd = mock_run.call_args[0][0]
            assert "-s" in cmd
            assert "-a" not in cmd

    def test_force_tag(self):
        with patch("commit_and_tag_version.git.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            git_tag("v1.0.0", "release", force=True)
            cmd = mock_run.call_args[0][0]
            assert "-f" in cmd


class TestGetSemverTags:
    def test_returns_sorted_tags(self):
        tag_output = "v2.0.0\nv1.0.0\nv1.5.0\n"
        with patch("commit_and_tag_version.git.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout=tag_output, stderr="")
            tags = get_semver_tags("v")
            assert tags[0] == "2.0.0"
            assert tags[-1] == "1.0.0"

    def test_strips_tag_prefix(self):
        tag_output = "v1.0.0\n"
        with patch("commit_and_tag_version.git.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout=tag_output, stderr="")
            tags = get_semver_tags("v")
            assert tags == ["1.0.0"]


class TestGetLatestSemverTag:
    def test_returns_latest(self):
        tag_output = "v1.0.0\nv2.0.0\nv1.5.0\n"
        with patch("commit_and_tag_version.git.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout=tag_output, stderr="")
            latest = get_latest_semver_tag("v")
            assert latest == "2.0.0"

    def test_returns_fallback_when_no_tags(self):
        with patch("commit_and_tag_version.git.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            latest = get_latest_semver_tag("v")
            assert latest == "1.0.0"

    def test_filters_prerelease_by_channel(self):
        tag_output = "v1.0.1-alpha.0\nv1.0.1-beta.0\nv1.0.0\n"
        with patch("commit_and_tag_version.git.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout=tag_output, stderr="")
            latest = get_latest_semver_tag("v", prerelease="alpha")
            assert latest == "1.0.1-alpha.0"


class TestGitLogRaw:
    def test_returns_commit_messages(self):
        log_output = "feat: add feature\x00fix: fix bug\x00"
        with patch("commit_and_tag_version.git.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout=log_output, stderr="")
            messages = git_log_raw()
            assert len(messages) == 2
