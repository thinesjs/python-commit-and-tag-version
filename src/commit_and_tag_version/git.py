import re
import subprocess

import semver


def _run_git(args: list[str], dry_run: bool = False) -> str:
    if dry_run:
        return ""
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def git_add(files: list[str], dry_run: bool = False) -> None:
    _run_git(["add", *files], dry_run=dry_run)


def git_commit(
    message: str,
    sign: bool = False,
    signoff: bool = False,
    no_verify: bool = False,
    dry_run: bool = False,
    files: list[str] | None = None,
) -> None:
    cmd = ["commit"]
    if sign:
        cmd.append("--gpg-sign")
    if signoff:
        cmd.append("--signoff")
    if no_verify:
        cmd.append("--no-verify")
    cmd.extend(["-m", message])
    if files:
        cmd.extend(files)
    _run_git(cmd, dry_run=dry_run)


def git_tag(
    name: str,
    message: str,
    sign: bool = False,
    force: bool = False,
    dry_run: bool = False,
) -> None:
    cmd = ["tag"]
    if sign:
        cmd.append("-s")
    else:
        cmd.append("-a")
    if force:
        cmd.append("-f")
    cmd.extend([name, "-m", message])
    _run_git(cmd, dry_run=dry_run)


def get_current_branch() -> str:
    return _run_git(["rev-parse", "--abbrev-ref", "HEAD"]).strip()


def get_semver_tags(tag_prefix: str, prerelease: str | None = None) -> list[str]:
    output = _run_git(["tag", "-l", f"{tag_prefix}*"])
    if not output.strip():
        return []

    tags = []
    prefix_pattern = re.compile(f"^{re.escape(tag_prefix)}")
    for line in output.strip().split("\n"):
        stripped = prefix_pattern.sub("", line.strip())
        if semver.Version.is_valid(stripped):
            tags.append(stripped)

    if prerelease is not None:
        filtered = []
        for tag in tags:
            v = semver.Version.parse(tag)
            if v.prerelease is None:
                filtered.append(tag)
            elif v.prerelease.split(".")[0] == prerelease:
                filtered.append(tag)
        tags = filtered

    tags.sort(key=lambda t: semver.Version.parse(t), reverse=True)
    return tags


def get_latest_semver_tag(tag_prefix: str, prerelease: str | None = None) -> str:
    tags = get_semver_tags(tag_prefix, prerelease=prerelease)
    if not tags:
        return "1.0.0"
    return tags[0]


def git_log_raw(
    from_tag: str | None = None,
    to: str = "HEAD",
    path: str | None = None,
) -> list[str]:
    if from_tag:
        range_spec = f"{from_tag}..{to}"
    else:
        range_spec = to
    cmd = ["log", range_spec, "--format=%B%x00"]
    if path:
        cmd.extend(["--", path])
    output = _run_git(cmd)
    if not output.strip():
        return []
    messages = [m.strip() for m in output.split("\x00") if m.strip()]
    return messages
