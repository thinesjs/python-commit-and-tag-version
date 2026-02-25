import os
import re

from commit_and_tag_version.updaters.csproj import CsprojUpdater
from commit_and_tag_version.updaters.gradle import GradleUpdater
from commit_and_tag_version.updaters.json_updater import JsonUpdater
from commit_and_tag_version.updaters.maven import MavenUpdater
from commit_and_tag_version.updaters.openapi import OpenApiUpdater
from commit_and_tag_version.updaters.plain_text import PlainTextUpdater
from commit_and_tag_version.updaters.python_updater import PythonUpdater
from commit_and_tag_version.updaters.yaml_updater import YamlUpdater

UPDATERS_BY_TYPE = {
    "json": JsonUpdater,
    "plain-text": PlainTextUpdater,
    "maven": MavenUpdater,
    "gradle": GradleUpdater,
    "csproj": CsprojUpdater,
    "yaml": YamlUpdater,
    "openapi": OpenApiUpdater,
    "python": PythonUpdater,
}

JSON_BUMP_FILES = [
    "package.json",
    "bower.json",
    "manifest.json",
    "package-lock.json",
    "npm-shrinkwrap.json",
]
PLAIN_TEXT_BUMP_FILES = ["VERSION.txt", "version.txt"]


def _get_updater_by_type(updater_type: str):
    cls = UPDATERS_BY_TYPE.get(updater_type)
    if cls is None:
        raise ValueError(f"Unable to locate updater for provided type ({updater_type}).")
    return cls()


def _get_updater_by_filename(filename: str):
    basename = os.path.basename(filename)
    if basename in JSON_BUMP_FILES:
        return _get_updater_by_type("json")
    if basename in PLAIN_TEXT_BUMP_FILES:
        return _get_updater_by_type("plain-text")
    if re.search(r"pom\.xml", filename):
        return _get_updater_by_type("maven")
    if re.search(r"build\.gradle", filename):
        return _get_updater_by_type("gradle")
    if filename.endswith(".csproj"):
        return _get_updater_by_type("csproj")
    if re.search(r"openapi\.ya?ml", filename):
        return _get_updater_by_type("openapi")
    if re.search(r"\.ya?ml$", filename):
        return _get_updater_by_type("yaml")
    if re.search(r"pyproject\.toml", filename):
        return _get_updater_by_type("python")
    return None


def resolve_updater_object(arg: str | dict) -> dict | None:
    if isinstance(arg, str):
        updater = _get_updater_by_filename(arg)
        if updater is None:
            return None
        return {"filename": arg, "updater": updater}

    filename = arg.get("filename", "")
    updater_type = arg.get("type")

    if updater_type:
        updater = _get_updater_by_type(updater_type)
    else:
        updater = _get_updater_by_filename(filename)

    if updater is None:
        return None

    return {"filename": filename, "updater": updater}
