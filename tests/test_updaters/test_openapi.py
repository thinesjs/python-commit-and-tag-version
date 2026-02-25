from pathlib import Path

from commit_and_tag_version.updaters.openapi import OpenApiUpdater

FIXTURES = Path(__file__).parent.parent / "fixtures"


def test_read_version():
    updater = OpenApiUpdater()
    contents = (FIXTURES / "openapi-1.2.3.yaml").read_text()
    assert updater.read_version(contents) == "1.2.3"


def test_write_version():
    updater = OpenApiUpdater()
    contents = (FIXTURES / "openapi-1.2.3.yaml").read_text()
    result = updater.write_version(contents, "2.0.0")
    assert updater.read_version(result) == "2.0.0"


def test_preserves_other_fields():
    updater = OpenApiUpdater()
    contents = (FIXTURES / "openapi-1.2.3.yaml").read_text()
    result = updater.write_version(contents, "2.0.0")
    assert "Test API" in result
