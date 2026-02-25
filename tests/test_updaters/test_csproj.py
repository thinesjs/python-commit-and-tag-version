from pathlib import Path

import pytest

from commit_and_tag_version.updaters.csproj import CsprojUpdater

FIXTURES = Path(__file__).parent.parent / "fixtures"


def test_read_version():
    updater = CsprojUpdater()
    contents = (FIXTURES / "Project-6.3.1.csproj").read_text()
    assert updater.read_version(contents) == "6.3.1"


def test_write_version():
    updater = CsprojUpdater()
    contents = (FIXTURES / "Project-6.3.1.csproj").read_text()
    result = updater.write_version(contents, "6.4.0")
    assert "<Version>6.4.0</Version>" in result


def test_raises_on_missing_version():
    updater = CsprojUpdater()
    with pytest.raises(ValueError):
        updater.read_version("<Project></Project>")
