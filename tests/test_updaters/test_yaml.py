from pathlib import Path

from commit_and_tag_version.updaters.yaml_updater import YamlUpdater

FIXTURES = Path(__file__).parent.parent / "fixtures"


def test_read_version():
    updater = YamlUpdater()
    contents = (FIXTURES / "pubspec-6.3.1.yaml").read_text()
    assert updater.read_version(contents) == "6.3.1"


def test_write_version():
    updater = YamlUpdater()
    contents = (FIXTURES / "pubspec-6.3.1.yaml").read_text()
    result = updater.write_version(contents, "7.0.0")
    assert updater.read_version(result) == "7.0.0"


def test_preserves_other_fields():
    updater = YamlUpdater()
    contents = (FIXTURES / "pubspec-6.3.1.yaml").read_text()
    result = updater.write_version(contents, "7.0.0")
    assert "test_app" in result
