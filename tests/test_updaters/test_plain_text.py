from commit_and_tag_version.updaters.plain_text import PlainTextUpdater


def test_read_version():
    updater = PlainTextUpdater()
    assert updater.read_version("1.0.0") == "1.0.0"


def test_write_version():
    updater = PlainTextUpdater()
    assert updater.write_version("1.0.0", "2.0.0") == "2.0.0"


def test_read_version_strips_whitespace():
    updater = PlainTextUpdater()
    assert updater.read_version("  1.0.0  \n") == "1.0.0"
