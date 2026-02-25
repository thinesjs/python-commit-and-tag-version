import json
from pathlib import Path

from commit_and_tag_version.updaters.json_updater import JsonUpdater

FIXTURES = Path(__file__).parent.parent / "fixtures"


def test_read_version():
    updater = JsonUpdater()
    contents = (FIXTURES / "package-1.0.0.json").read_text()
    assert updater.read_version(contents) == "1.0.0"


def test_write_version():
    updater = JsonUpdater()
    contents = (FIXTURES / "package-1.0.0.json").read_text()
    result = updater.write_version(contents, "2.0.0")
    assert '"version": "2.0.0"' in result


def test_preserves_indentation():
    updater = JsonUpdater()
    contents = '{\n    "version": "1.0.0"\n}\n'
    result = updater.write_version(contents, "2.0.0")
    assert '    "version"' in result


def test_preserves_trailing_newline():
    updater = JsonUpdater()
    contents = '{"version": "1.0.0"}\n'
    result = updater.write_version(contents, "2.0.0")
    assert result.endswith("\n")
    assert not result.endswith("\n\n")


def test_package_lock_v2():
    updater = JsonUpdater()
    contents = (
        '{\n  "version": "1.0.0",\n  "packages":'
        ' {\n    "": {\n      "version": "1.0.0"\n    }\n  }\n}\n'
    )
    result = updater.write_version(contents, "2.0.0")
    parsed = json.loads(result)
    assert parsed["version"] == "2.0.0"
    assert parsed["packages"][""]["version"] == "2.0.0"


def test_is_private():
    updater = JsonUpdater()
    assert updater.is_private('{"private": true}') is True
    assert updater.is_private('{"private": false}') is False
    assert updater.is_private('{"name": "test"}') is False
