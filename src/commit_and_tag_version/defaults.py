from commit_and_tag_version.models import Config, ScriptsConfig, SkipConfig

DEFAULT_PACKAGE_FILES: list[str] = ["package.json", "bower.json", "manifest.json"]

DEFAULT_BUMP_FILES: list[str] = [
    "package.json",
    "bower.json",
    "manifest.json",
    "package-lock.json",
    "npm-shrinkwrap.json",
]

DEFAULT_INFILE = "CHANGELOG.md"
DEFAULT_TAG_PREFIX = "v"
DEFAULT_RELEASE_COUNT = 1
DEFAULT_PRESET = "conventionalcommits"

DEFAULT_RELEASE_COMMIT_MESSAGE_FORMAT = "chore(release): {{currentTag}}"

DEFAULT_HEADER = (
    "# Changelog\n\nAll notable changes to this project will be documented in this file. "
    "See [commit-and-tag-version](https://github.com/absolute-version/commit-and-tag-version) "
    "for commit guidelines.\n"
)

DEFAULT_COMMIT_TYPES: list[dict] = [
    {"type": "feat", "section": "Features"},
    {"type": "fix", "section": "Bug Fixes"},
    {"type": "chore", "section": "Chores", "hidden": True},
    {"type": "docs", "section": "Documentation", "hidden": True},
    {"type": "style", "section": "Styles", "hidden": True},
    {"type": "refactor", "section": "Refactoring", "hidden": True},
    {"type": "perf", "section": "Performance", "hidden": True},
    {"type": "test", "section": "Tests", "hidden": True},
    {"type": "build", "section": "Build System", "hidden": True},
    {"type": "ci", "section": "CI", "hidden": True},
]


def get_default_config() -> Config:
    return Config(
        package_files=list(DEFAULT_PACKAGE_FILES),
        bump_files=list(DEFAULT_BUMP_FILES),
        infile=DEFAULT_INFILE,
        tag_prefix=DEFAULT_TAG_PREFIX,
        preset=DEFAULT_PRESET,
        release_as=None,
        prerelease=None,
        sign=False,
        signoff=False,
        no_verify=False,
        commit_all=False,
        first_release=False,
        dry_run=False,
        silent=False,
        tag_force=False,
        release_count=DEFAULT_RELEASE_COUNT,
        skip=SkipConfig(),
        scripts=ScriptsConfig(),
        header=DEFAULT_HEADER,
        commit_url_format=None,
        compare_url_format=None,
        issue_url_format=None,
        release_commit_message_format=DEFAULT_RELEASE_COMMIT_MESSAGE_FORMAT,
        git_tag_fallback=True,
        path=None,
        types=None,
    )
