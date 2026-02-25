from commit_and_tag_version.defaults import (
    DEFAULT_BUMP_FILES,
    DEFAULT_COMMIT_TYPES,
    DEFAULT_HEADER,
    DEFAULT_INFILE,
    DEFAULT_PACKAGE_FILES,
    DEFAULT_TAG_PREFIX,
    get_default_config,
)


def test_default_package_files():
    assert DEFAULT_PACKAGE_FILES == ["package.json", "bower.json", "manifest.json"]


def test_default_bump_files_includes_package_files():
    for f in DEFAULT_PACKAGE_FILES:
        assert f in DEFAULT_BUMP_FILES
    assert "package-lock.json" in DEFAULT_BUMP_FILES
    assert "npm-shrinkwrap.json" in DEFAULT_BUMP_FILES


def test_default_tag_prefix():
    assert DEFAULT_TAG_PREFIX == "v"


def test_default_infile():
    assert DEFAULT_INFILE == "CHANGELOG.md"


def test_default_header_contains_changelog():
    assert "# Changelog" in DEFAULT_HEADER


def test_default_commit_types():
    type_names = [t["type"] for t in DEFAULT_COMMIT_TYPES]
    assert "feat" in type_names
    assert "fix" in type_names


def test_get_default_config_returns_config():
    config = get_default_config()
    assert config.tag_prefix == "v"
    assert config.infile == "CHANGELOG.md"
    assert config.dry_run is False
    assert config.first_release is False
