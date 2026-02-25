from pathlib import Path

import pytest

from commit_and_tag_version.updaters.gradle import GradleUpdater

FIXTURES = Path(__file__).parent.parent / "fixtures"


def test_read_version():
    updater = GradleUpdater()
    contents = (FIXTURES / "build-6.3.1.gradle.kts").read_text()
    assert updater.read_version(contents) == "6.3.1"


def test_write_version():
    updater = GradleUpdater()
    contents = (FIXTURES / "build-6.3.1.gradle.kts").read_text()
    result = updater.write_version(contents, "6.4.0")
    assert updater.read_version(result) == "6.4.0"


def test_raises_on_missing_version():
    updater = GradleUpdater()
    with pytest.raises(ValueError):
        updater.read_version("plugins { }")
