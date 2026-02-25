from commit_and_tag_version.checkpoint import checkpoint


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
