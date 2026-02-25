import re

import semver as semver_mod

from commit_and_tag_version.models import ParsedCommit

COMMIT_PATTERN = re.compile(
    r"^(?P<type>\w+)(?:\((?P<scope>[^)]+)\))?(?P<breaking>!)?:\s*(?P<subject>.+)"
)
BREAKING_CHANGE_PATTERN = re.compile(r"^BREAKING[\- ]CHANGE:\s*(?P<note>.+)", re.MULTILINE)
ISSUE_PATTERN = re.compile(r"#(\d+)")


def parse_commit(raw: str) -> ParsedCommit | None:
    lines = raw.strip().split("\n")
    if not lines:
        return None

    header = lines[0]
    match = COMMIT_PATTERN.match(header)
    if not match:
        return None

    body_lines = []
    if len(lines) > 2:
        body_lines = lines[2:]
    body = "\n".join(body_lines) if body_lines else None
    full_text = raw.strip()

    breaking = match.group("breaking") == "!"
    breaking_note = None

    breaking_match = BREAKING_CHANGE_PATTERN.search(full_text)
    if breaking_match:
        breaking = True
        breaking_note = breaking_match.group("note").strip()

    references = []
    for issue_match in ISSUE_PATTERN.finditer(full_text):
        ref = f"#{issue_match.group(1)}"
        if ref not in references:
            references.append(ref)

    return ParsedCommit(
        type=match.group("type"),
        scope=match.group("scope"),
        subject=match.group("subject").strip(),
        body=body,
        breaking=breaking,
        breaking_note=breaking_note,
        references=references,
        raw=raw.strip(),
    )


def recommend_bump(
    commits: list[ParsedCommit | None],
    current_version: str = "1.0.0",
) -> str:
    has_breaking = False
    has_feat = False

    for commit in commits:
        if commit is None:
            continue
        if commit.breaking:
            has_breaking = True
        if commit.type == "feat":
            has_feat = True

    pre_major = semver_mod.Version.parse(current_version) < semver_mod.Version.parse("1.0.0")

    if has_breaking:
        return "minor" if pre_major else "major"
    if has_feat:
        return "minor"
    return "patch"
