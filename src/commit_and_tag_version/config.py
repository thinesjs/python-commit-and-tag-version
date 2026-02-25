import json
from pathlib import Path

from commit_and_tag_version.defaults import get_default_config
from commit_and_tag_version.models import Config

try:
    import tomllib
except ModuleNotFoundError:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ModuleNotFoundError:
        tomllib = None  # type: ignore[assignment]

CAMEL_TO_SNAKE: dict[str, str] = {
    "tagPrefix": "tag_prefix",
    "releaseAs": "release_as",
    "noVerify": "no_verify",
    "commitAll": "commit_all",
    "firstRelease": "first_release",
    "dryRun": "dry_run",
    "tagForce": "tag_force",
    "releaseCount": "release_count",
    "releaseCommitMessageFormat": "release_commit_message_format",
    "commitUrlFormat": "commit_url_format",
    "compareUrlFormat": "compare_url_format",
    "issueUrlFormat": "issue_url_format",
    "gitTagFallback": "git_tag_fallback",
    "packageFiles": "package_files",
    "bumpFiles": "bump_files",
}


def _normalize_keys(raw: dict) -> dict:
    normalized: dict = {}
    for key, value in raw.items():
        snake_key = CAMEL_TO_SNAKE.get(key, key)
        normalized[snake_key] = value
    return normalized


def _load_json_file(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_pyproject_toml(path: Path) -> dict:
    if tomllib is None:
        return {}
    with open(path, "rb") as f:
        data = tomllib.load(f)
    return data.get("tool", {}).get("commit-and-tag-version", {})


def _discover_file_config(config_path: str | None = None) -> dict:
    if config_path:
        path = Path(config_path)
        if path.exists():
            return _normalize_keys(_load_json_file(path))
        return {}

    cwd = Path.cwd()

    versionrc = cwd / ".versionrc"
    if versionrc.exists():
        return _normalize_keys(_load_json_file(versionrc))

    versionrc_json = cwd / ".versionrc.json"
    if versionrc_json.exists():
        return _normalize_keys(_load_json_file(versionrc_json))

    pyproject = cwd / "pyproject.toml"
    if pyproject.exists():
        raw = _load_pyproject_toml(pyproject)
        if raw:
            return _normalize_keys(raw)

    return {}


def _apply_to_config(config: Config, overrides: dict) -> None:
    skip_raw = overrides.pop("skip", None)
    scripts_raw = overrides.pop("scripts", None)

    for key, value in overrides.items():
        if hasattr(config, key):
            setattr(config, key, value)

    if skip_raw and isinstance(skip_raw, dict):
        for k, v in skip_raw.items():
            if hasattr(config.skip, k):
                setattr(config.skip, k, v)

    if scripts_raw and isinstance(scripts_raw, dict):
        for k, v in scripts_raw.items():
            if hasattr(config.scripts, k):
                setattr(config.scripts, k, v)


def load_config(cli_args: dict) -> Config:
    config = get_default_config()

    config_path = cli_args.pop("config", None)
    file_overrides = _discover_file_config(config_path)
    _apply_to_config(config, file_overrides)

    cli_overrides = {k: v for k, v in cli_args.items() if v is not None}
    _apply_to_config(config, cli_overrides)

    return config
