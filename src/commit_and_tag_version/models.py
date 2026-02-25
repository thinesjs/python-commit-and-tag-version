from dataclasses import dataclass


@dataclass
class SkipConfig:
    bump: bool = False
    changelog: bool = False
    commit: bool = False
    tag: bool = False


@dataclass
class ScriptsConfig:
    prerelease: str | None = None
    prebump: str | None = None
    postbump: str | None = None
    prechangelog: str | None = None
    postchangelog: str | None = None
    precommit: str | None = None
    postcommit: str | None = None
    pretag: str | None = None
    posttag: str | None = None


@dataclass
class ParsedCommit:
    type: str
    scope: str | None
    subject: str
    body: str | None
    breaking: bool
    breaking_note: str | None
    references: list[str]
    raw: str


@dataclass
class CommitType:
    type: str
    section: str
    hidden: bool = False


@dataclass
class Config:
    package_files: list[str | dict]
    bump_files: list[str | dict]
    infile: str
    tag_prefix: str
    preset: str
    release_as: str | None
    prerelease: str | None
    sign: bool
    signoff: bool
    no_verify: bool
    commit_all: bool
    first_release: bool
    dry_run: bool
    silent: bool
    tag_force: bool
    release_count: int
    skip: SkipConfig
    scripts: ScriptsConfig
    header: str
    commit_url_format: str | None
    compare_url_format: str | None
    issue_url_format: str | None
    release_commit_message_format: str
    git_tag_fallback: bool = True
    path: str | None = None
    types: list[dict] | None = None
