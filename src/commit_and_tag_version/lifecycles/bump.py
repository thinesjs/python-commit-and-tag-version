from pathlib import Path

import semver

from commit_and_tag_version.checkpoint import checkpoint
from commit_and_tag_version.commit_parser import parse_commit, recommend_bump
from commit_and_tag_version.git import get_semver_tags, git_log_raw
from commit_and_tag_version.models import Config
from commit_and_tag_version.run_lifecycle_script import run_lifecycle_script
from commit_and_tag_version.updaters import resolve_updater_object

_updated_configs: dict[str, bool] = {}

_TYPE_LIST: tuple[str, ...] = ("patch", "minor", "major")


def get_updated_configs() -> dict[str, bool]:
    return dict(_updated_configs)


def _get_current_active_type(current_version: str) -> str | None:
    v = semver.Version.parse(current_version)
    if v.patch:
        return "patch"
    if v.minor:
        return "minor"
    if v.major:
        return "major"
    return None


def _get_type_priority(release_type: str) -> int:
    return _TYPE_LIST.index(release_type)


def _should_continue_prerelease(current_version: str, expected_type: str) -> bool:
    return _get_current_active_type(current_version) == expected_type


def _get_release_type(prerelease: str | None, expected_type: str, current_version: str) -> str:
    if prerelease is None:
        return expected_type

    v = semver.Version.parse(current_version)
    if v.prerelease is not None:
        active = _get_current_active_type(current_version)
        if _should_continue_prerelease(current_version, expected_type) or (
            active is not None
            and expected_type in _TYPE_LIST
            and _get_type_priority(active) > _get_type_priority(expected_type)
        ):
            return "prerelease"

    match expected_type:
        case "major":
            return "premajor"
        case "minor":
            return "preminor"
        case "patch":
            return "prepatch"
        case _:
            return "prerelease"


def _increment_version(
    v: semver.Version, release_type: str, prerelease_id: str | None
) -> semver.Version:
    match release_type:
        case "major":
            if v.minor != 0 or v.patch != 0 or v.prerelease is None:
                return v.bump_major()
            return semver.Version(v.major, 0, 0)
        case "minor":
            if v.patch != 0 or v.prerelease is None:
                return v.bump_minor()
            return semver.Version(v.major, v.minor, 0)
        case "patch":
            if v.prerelease is None:
                return v.bump_patch()
            return semver.Version(v.major, v.minor, v.patch)
        case "premajor":
            bumped = v.bump_major()
            return semver.Version(bumped.major, bumped.minor, bumped.patch, f"{prerelease_id}.0")
        case "preminor":
            bumped = v.bump_minor()
            return semver.Version(bumped.major, bumped.minor, bumped.patch, f"{prerelease_id}.0")
        case "prepatch":
            bumped = v.bump_patch()
            return semver.Version(bumped.major, bumped.minor, bumped.patch, f"{prerelease_id}.0")
        case "prerelease":
            if v.prerelease is not None:
                parts = v.prerelease.split(".")
                if len(parts) >= 2 and parts[-1].isdigit():
                    num = int(parts[-1]) + 1
                    new_pre = ".".join(parts[:-1]) + f".{num}"
                else:
                    new_pre = f"{v.prerelease}.1"
                return semver.Version(v.major, v.minor, v.patch, new_pre)
            bumped = v.bump_patch()
            return semver.Version(bumped.major, bumped.minor, bumped.patch, f"{prerelease_id}.0")
        case _:
            return v.bump_patch()


def _resolve_unique_prerelease_version(
    proposed: semver.Version, tag_prefix: str, prerelease_id: str
) -> semver.Version:
    existing_tags = get_semver_tags(tag_prefix, prerelease=prerelease_id)
    existing_versions = {semver.Version.parse(t) for t in existing_tags}

    current = proposed
    while current in existing_versions:
        current = _increment_version(current, "prerelease", prerelease_id)

    return current


def _update_configs(config: Config, new_version: str) -> None:
    global _updated_configs

    all_files = list(config.bump_files or [])

    for entry in all_files:
        resolved = resolve_updater_object(entry)
        if resolved is None:
            continue

        filename = resolved["filename"]
        updater = resolved["updater"]
        filepath = Path(filename)

        if not filepath.exists():
            continue

        contents = filepath.read_text(encoding="utf-8")
        if updater.is_private(contents):
            continue

        new_contents = updater.write_version(contents, new_version)

        if not config.dry_run:
            filepath.write_text(new_contents, encoding="utf-8")

        _updated_configs[filename] = True
        checkpoint(
            "bumping version in %s from %s to %s",
            [filename, updater.read_version(contents), new_version],
            silent=config.silent,
            dry_run=config.dry_run,
        )


def bump(config: Config, version: str) -> str:
    global _updated_configs
    _updated_configs = {}

    if config.first_release:
        checkpoint(
            "skip %s (first release)",
            ["version bump"],
            silent=config.silent,
            dry_run=config.dry_run,
        )
        return version

    run_lifecycle_script(config.scripts, "prerelease", silent=config.silent, dry_run=config.dry_run)
    hook_result = run_lifecycle_script(
        config.scripts, "prebump", silent=config.silent, dry_run=config.dry_run
    )
    if hook_result:
        try:
            semver.Version.parse(hook_result)
            new_version = hook_result
            _update_configs(config, new_version)
            run_lifecycle_script(
                config.scripts, "postbump", silent=config.silent, dry_run=config.dry_run
            )
            return new_version
        except ValueError:
            pass

    current = semver.Version.parse(version)

    if config.release_as:
        release_as = config.release_as.lower()
        if release_as in ("major", "minor", "patch"):
            release_type = _get_release_type(config.prerelease, release_as, version)
        else:
            new_version = config.release_as
            _update_configs(config, new_version)
            run_lifecycle_script(
                config.scripts, "postbump", silent=config.silent, dry_run=config.dry_run
            )
            return new_version
    else:
        tag = f"{config.tag_prefix}{version}" if config.tag_prefix else version
        raw_messages = git_log_raw(from_tag=tag, path=config.path)
        commits = [parse_commit(m) for m in raw_messages]
        expected = recommend_bump(commits, version)
        release_type = _get_release_type(config.prerelease, expected, version)

    new_ver = _increment_version(current, release_type, config.prerelease)

    if config.prerelease:
        new_ver = _resolve_unique_prerelease_version(new_ver, config.tag_prefix, config.prerelease)

    new_version = str(new_ver)
    _update_configs(config, new_version)

    run_lifecycle_script(config.scripts, "postbump", silent=config.silent, dry_run=config.dry_run)

    return new_version
