from unittest.mock import patch

from commit_and_tag_version.checkpoint import checkpoint, print_error


class TestCheckpoint:
    def test_normal_uses_checkmark(self, capsys):
        checkpoint("test %s", ["value"], silent=False, dry_run=False)
        captured = capsys.readouterr()
        assert "\u2713" in captured.err
        assert "\u2299" not in captured.err

    def test_dry_run_uses_circle(self, capsys):
        checkpoint("test %s", ["value"], silent=False, dry_run=True)
        captured = capsys.readouterr()
        assert "\u2299" in captured.err
        assert "\u2713" not in captured.err

    def test_silent_suppresses_output(self, capsys):
        checkpoint("test %s", ["value"], silent=True, dry_run=False)
        captured = capsys.readouterr()
        assert captured.err == ""

    def test_no_ansi_codes_when_stderr_is_not_a_tty(self, capsys, monkeypatch):
        monkeypatch.delenv("NO_COLOR", raising=False)
        monkeypatch.delenv("FORCE_COLOR", raising=False)
        checkpoint("bumping version in %s from %s to %s", ["x", "1.0.0", "1.0.1"])
        captured = capsys.readouterr()
        assert "\033[" not in captured.err
        assert "bumping version in x from 1.0.0 to 1.0.1" in captured.err

    def test_ansi_codes_when_stderr_is_a_tty(self, capsys, monkeypatch):
        monkeypatch.delenv("NO_COLOR", raising=False)
        monkeypatch.delenv("FORCE_COLOR", raising=False)
        with patch("sys.stderr.isatty", return_value=True):
            checkpoint("bumping version in %s", ["x"])
        captured = capsys.readouterr()
        assert "\033[1mx\033[0m" in captured.err

    def test_no_color_env_var_disables_ansi_even_in_tty(self, capsys, monkeypatch):
        monkeypatch.setenv("NO_COLOR", "1")
        monkeypatch.delenv("FORCE_COLOR", raising=False)
        with patch("sys.stderr.isatty", return_value=True):
            checkpoint("bumping version in %s", ["x"])
        captured = capsys.readouterr()
        assert "\033[" not in captured.err
        assert "bumping version in x" in captured.err

    def test_force_color_env_var_enables_ansi_without_tty(self, capsys, monkeypatch):
        monkeypatch.delenv("NO_COLOR", raising=False)
        monkeypatch.setenv("FORCE_COLOR", "1")
        checkpoint("bumping version in %s", ["x"])
        captured = capsys.readouterr()
        assert "\033[1mx\033[0m" in captured.err

    def test_no_color_takes_precedence_over_force_color(self, capsys, monkeypatch):
        monkeypatch.setenv("NO_COLOR", "1")
        monkeypatch.setenv("FORCE_COLOR", "1")
        with patch("sys.stderr.isatty", return_value=True):
            checkpoint("bumping version in %s", ["x"])
        captured = capsys.readouterr()
        assert "\033[" not in captured.err

    def test_print_error_no_ansi_when_stderr_is_not_a_tty(self, capsys, monkeypatch):
        monkeypatch.delenv("NO_COLOR", raising=False)
        monkeypatch.delenv("FORCE_COLOR", raising=False)
        print_error("something went wrong")
        captured = capsys.readouterr()
        assert "\033[" not in captured.err
        assert "something went wrong" in captured.err

    def test_print_error_uses_red_when_stderr_is_a_tty(self, capsys, monkeypatch):
        monkeypatch.delenv("NO_COLOR", raising=False)
        monkeypatch.delenv("FORCE_COLOR", raising=False)
        with patch("sys.stderr.isatty", return_value=True):
            print_error("oops")
        captured = capsys.readouterr()
        assert "\033[31m" in captured.err
        assert "\033[0m" in captured.err
        assert "oops" in captured.err

    def test_print_error_silent_suppresses_output(self, capsys):
        print_error("oops", silent=True)
        captured = capsys.readouterr()
        assert captured.err == ""
