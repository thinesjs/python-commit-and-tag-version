"""Versioning using semver and CHANGELOG generation powered by Conventional Commits."""

from pathlib import Path

from commit_and_tag_version.checkpoint import print_error
from commit_and_tag_version.git import get_latest_semver_tag
from commit_and_tag_version.lifecycles.bump import bump
from commit_and_tag_version.lifecycles.changelog import (
    START_OF_LAST_RELEASE_PATTERN,
    changelog,
)
from commit_and_tag_version.lifecycles.commit import commit
from commit_and_tag_version.lifecycles.tag import tag
from commit_and_tag_version.models import Config
from commit_and_tag_version.updaters import resolve_updater_object


def commit_and_tag_version(config: Config) -> None:
    if config.header and START_OF_LAST_RELEASE_PATTERN.search(config.header):
        raise ValueError(
            f"custom changelog header must not match {START_OF_LAST_RELEASE_PATTERN.pattern}"
        )

    pkg = None
    version = None

    for package_file in config.package_files:
        updater_obj = resolve_updater_object(package_file)
        if not updater_obj:
            continue
        pkg_path = Path.cwd() / updater_obj["filename"]
        try:
            contents = pkg_path.read_text(encoding="utf-8")
            updater = updater_obj["updater"]
            pkg = {
                "version": updater.read_version(contents),
                "private": (
                    updater.is_private(contents) if hasattr(updater, "is_private") else False
                ),
            }
            version = pkg["version"]
            break
        except (FileNotFoundError, KeyError, ValueError):
            continue

    all_skipped = (
        config.skip.bump and config.skip.changelog and config.skip.commit and config.skip.tag
    )

    if version is None:
        if all_skipped:
            return
        if config.git_tag_fallback:
            version = get_latest_semver_tag(config.tag_prefix)
        else:
            raise RuntimeError("no package file found")

    if all_skipped:
        return

    try:
        new_version = bump(config, version) if not config.skip.bump else version
        changelog(config, new_version)
        commit(config, new_version)
        tag(new_version, pkg["private"] if pkg else False, config)
    except Exception as err:
        print_error(str(err), silent=config.silent)
        raise
