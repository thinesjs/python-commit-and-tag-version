import re
from datetime import date as date_type
from pathlib import Path

from commit_and_tag_version.checkpoint import checkpoint
from commit_and_tag_version.commit_parser import parse_commit
from commit_and_tag_version.defaults import DEFAULT_COMMIT_TYPES, DEFAULT_HEADER
from commit_and_tag_version.git import get_semver_tags, git_log_raw
from commit_and_tag_version.models import Config, ParsedCommit
from commit_and_tag_version.run_lifecycle_script import run_lifecycle_script
from commit_and_tag_version.write_file import write_file

START_OF_LAST_RELEASE_PATTERN = re.compile(
    r"^#{2,3}\s+\[?\d+\.\d+\.\d+",
    re.MULTILINE,
)


def generate_changelog_entry(
    version: str,
    commits: list[ParsedCommit],
    date: date_type | None = None,
    tag_prefix: str = "v",
    types: list[dict] | None = None,
) -> str:
    if date is None:
        date = date_type.today()

    if types is None:
        types = DEFAULT_COMMIT_TYPES

    type_map: dict[str, str] = {}
    hidden_types: set[str] = set()
    for t in types:
        type_map[t["type"]] = t["section"]
        if t.get("hidden", False):
            hidden_types.add(t["type"])

    sections: dict[str, list[str]] = {}
    breaking_changes: list[str] = []

    for commit in commits:
        if commit.breaking and commit.breaking_note:
            scope_prefix = f"**{commit.scope}:** " if commit.scope else ""
            breaking_changes.append(f"* {scope_prefix}{commit.breaking_note}")

        if commit.type in hidden_types:
            continue

        section = type_map.get(commit.type)
        if section is None:
            continue

        scope_prefix = f"**{commit.scope}:** " if commit.scope else ""
        line = f"* {scope_prefix}{commit.subject}"

        if section not in sections:
            sections[section] = []
        sections[section].append(line)

    date_str = date.strftime("%Y-%m-%d")
    lines = [f"## [{version}]({tag_prefix}{version}) ({date_str})", ""]

    section_order = [t["section"] for t in types if not t.get("hidden", False)]
    seen: set[str] = set()
    ordered_sections: list[str] = []
    for s in section_order:
        if s not in seen and s in sections:
            ordered_sections.append(s)
            seen.add(s)

    for section_name in ordered_sections:
        items = sections[section_name]
        lines.append(f"### {section_name}")
        lines.append("")
        lines.extend(items)
        lines.append("")

    if breaking_changes:
        lines.append("### BREAKING CHANGES")
        lines.append("")
        lines.extend(breaking_changes)
        lines.append("")

    return "\n".join(lines)


def _output_changelog(config: Config, entry: str) -> None:
    infile = Path(config.infile)
    header = config.header or DEFAULT_HEADER

    if not infile.exists():
        content = header + "\n" + entry
        write_file(infile, content, dry_run=config.dry_run)
        return

    existing = infile.read_text(encoding="utf-8")

    match = START_OF_LAST_RELEASE_PATTERN.search(existing)
    if match:
        insert_pos = match.start()
        front_matter = existing[:insert_pos]
        body = existing[insert_pos:]
        content = front_matter + entry + "\n" + body
    else:
        content = header + "\n" + entry + "\n" + existing

    write_file(infile, content, dry_run=config.dry_run)


def changelog(config: Config, new_version: str) -> None:
    if config.skip.changelog:
        return

    run_lifecycle_script(
        config.scripts, "prechangelog", silent=config.silent, dry_run=config.dry_run
    )

    checkpoint(
        "generating %s with %s",
        ["CHANGELOG", config.infile],
        silent=config.silent,
        dry_run=config.dry_run,
    )

    tag_prefix = config.tag_prefix
    existing_tags = get_semver_tags(tag_prefix, prerelease=config.prerelease)
    if existing_tags:
        previous_tag = existing_tags[0]
        from_tag = f"{tag_prefix}{previous_tag}"
    else:
        from_tag = None

    raw_messages = git_log_raw(from_tag=from_tag, path=config.path)
    commits = [parse_commit(m) for m in raw_messages]
    valid_commits = [c for c in commits if c is not None]

    entry = generate_changelog_entry(
        new_version,
        valid_commits,
        tag_prefix=tag_prefix,
        types=config.types,
    )

    _output_changelog(config, entry)

    run_lifecycle_script(
        config.scripts, "postchangelog", silent=config.silent, dry_run=config.dry_run
    )
