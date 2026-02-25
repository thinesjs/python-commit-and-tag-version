from pathlib import Path

import pytest

from commit_and_tag_version.updaters.maven import MavenUpdater

FIXTURES = Path(__file__).parent.parent / "fixtures"


def test_read_version():
    updater = MavenUpdater()
    contents = (FIXTURES / "pom-6.3.1.xml").read_text()
    assert updater.read_version(contents) == "6.3.1"


def test_write_version():
    updater = MavenUpdater()
    contents = (FIXTURES / "pom-6.3.1.xml").read_text()
    result = updater.write_version(contents, "6.4.0")
    assert updater.read_version(result) == "6.4.0"


def test_raises_on_missing_version():
    updater = MavenUpdater()
    with pytest.raises(ValueError):
        updater.read_version("<project></project>")
