from pathlib import Path

from commit_and_tag_version.updaters.python_updater import PythonUpdater

FIXTURES = Path(__file__).parent.parent / "fixtures"


def test_read_version():
    updater = PythonUpdater()
    contents = (FIXTURES / "pyproject-1.0.0.toml").read_text()
    assert updater.read_version(contents) == "1.0.0"


def test_write_version():
    updater = PythonUpdater()
    contents = (FIXTURES / "pyproject-1.0.0.toml").read_text()
    result = updater.write_version(contents, "2.0.0")
    assert updater.read_version(result) == "2.0.0"


def test_preserves_other_fields():
    updater = PythonUpdater()
    contents = (FIXTURES / "pyproject-1.0.0.toml").read_text()
    result = updater.write_version(contents, "2.0.0")
    assert 'name = "test"' in result
