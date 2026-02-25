import pytest

from commit_and_tag_version.updaters import resolve_updater_object


def test_resolve_string_package_json():
    result = resolve_updater_object("package.json")
    assert result is not None
    assert result["filename"] == "package.json"


def test_resolve_string_pom_xml():
    result = resolve_updater_object("pom.xml")
    assert result is not None


def test_resolve_string_build_gradle():
    result = resolve_updater_object("build.gradle")
    assert result is not None


def test_resolve_string_build_gradle_kts():
    result = resolve_updater_object("build.gradle.kts")
    assert result is not None


def test_resolve_string_csproj():
    result = resolve_updater_object("MyProject.csproj")
    assert result is not None


def test_resolve_string_version_txt():
    result = resolve_updater_object("VERSION.txt")
    assert result is not None


def test_resolve_string_yaml():
    result = resolve_updater_object("pubspec.yaml")
    assert result is not None


def test_resolve_string_openapi():
    result = resolve_updater_object("openapi.yaml")
    assert result is not None


def test_resolve_string_pyproject():
    result = resolve_updater_object("pyproject.toml")
    assert result is not None


def test_resolve_dict_with_type():
    result = resolve_updater_object({"filename": "custom.file", "type": "plain-text"})
    assert result is not None
    assert result["filename"] == "custom.file"


def test_resolve_unknown_file_returns_none():
    result = resolve_updater_object("unknown.xyz")
    assert result is None


def test_resolve_dict_with_unknown_type_raises():
    with pytest.raises(ValueError):
        resolve_updater_object({"filename": "test", "type": "nonexistent"})
