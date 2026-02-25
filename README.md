# commit-and-tag-version (Python)

A Python port of [commit-and-tag-version](https://github.com/absolute-version/commit-and-tag-version) — a utility for versioning using [semver](https://semver.org/) and CHANGELOG generation powered by [Conventional Commits](https://conventionalcommits.org).

[![CI](https://github.com/thinesjs/python-commit-and-tag-version/actions/workflows/ci.yml/badge.svg)](https://github.com/thinesjs/python-commit-and-tag-version/actions)
[![PyPI version](https://img.shields.io/pypi/v/commit-and-tag-version.svg)](https://pypi.org/project/commit-and-tag-version/)
[![Python](https://img.shields.io/pypi/pyversions/commit-and-tag-version.svg)](https://pypi.org/project/commit-and-tag-version/)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)

## How It Works

1. Follow the [Conventional Commits Specification](https://conventionalcommits.org) in your repository.
2. When you're ready to release, run `commit-and-tag-version`.

The tool will then:

1. Retrieve the current version from `packageFiles`, falling back to the last git tag.
2. **Bump** the version in `bumpFiles` based on your commits.
3. Generate a **changelog** based on your commits.
4. Create a new **commit** including your `bumpFiles` and updated CHANGELOG.
5. Create a new **tag** with the new version number.

### Version Bumps

| Commit Type | Version Bump |
|---|---|
| `fix:` | Patch (1.0.0 -> 1.0.1) |
| `feat:` | Minor (1.0.0 -> 1.1.0) |
| `feat!:` or `BREAKING CHANGE` | Major (1.0.0 -> 2.0.0) |

Breaking changes before v1.0.0 bump minor instead of major.

## Installing

```sh
pip install commit-and-tag-version
```

Or with a package manager:

```sh
# pipx (recommended for CLI tools)
pipx install commit-and-tag-version

# poetry
poetry add --group dev commit-and-tag-version

# uv
uv pip install commit-and-tag-version
```

## CLI Usage

### First Release

```sh
commit-and-tag-version --first-release
```

This will tag a release without bumping the version.

### Cutting Releases

```sh
commit-and-tag-version
```

As long as your git commit messages are conventional and accurate, the version bump is automatic and you get CHANGELOG generation for free.

After you cut a release, push the new git tag:

```sh
git push --follow-tags origin main
```

### Release as a Pre-Release

```sh
# unnamed prerelease: 1.0.1-0
commit-and-tag-version --prerelease

# named prerelease: 1.0.1-alpha.0
commit-and-tag-version --prerelease alpha
```

Prerelease tag collisions are automatically avoided by incrementing the numeric suffix.

### Release as a Target Type

```sh
# force a minor release
commit-and-tag-version --release-as minor

# force a specific version
commit-and-tag-version --release-as 1.1.0
```

You can combine `--release-as` and `--prerelease` to generate a pre-release for a specific version type.

### Dry Run Mode

```sh
commit-and-tag-version --dry-run
```

See what commands would be run, without committing to git or updating files.

### Skipping Lifecycle Steps

```sh
commit-and-tag-version --skip-changelog
commit-and-tag-version --skip-bump --skip-tag
```

Or via config:

```json
{
  "skip": {
    "changelog": true
  }
}
```

### Tag Prefix

Tags are prefixed with `v` by default. Customize with `--tag-prefix`:

```sh
commit-and-tag-version --tag-prefix "release/"
```

### Signing Commits and Tags

```sh
commit-and-tag-version --sign
```

### Prevent Git Hooks

```sh
commit-and-tag-version --no-verify
```

### Committing Generated Artifacts

Use `--commit-all` to include all staged changes in the release commit:

```sh
commit-and-tag-version --commit-all
```

### Tag Replacement

Use `--tag-force` to replace an existing tag (e.g., after amending a release):

```sh
commit-and-tag-version --skip-bump --tag-force
```

## File Type Support

`commit-and-tag-version` has built-in updaters for reading and writing versions in:

| File | Updater |
|---|---|
| `package.json`, `bower.json`, `manifest.json` | JSON |
| `pom.xml` | Maven |
| `build.gradle`, `build.gradle.kts` | Gradle |
| `*.csproj` | .NET |
| `*.yaml`, `*.yml` | YAML |
| `openapi.yaml`, `openapi.yml` | OpenAPI |
| `pyproject.toml` | Python (Poetry) |
| `VERSION.txt`, `version.txt` | Plain text |

Point to your project's version file(s) via config:

```json
{
  "packageFiles": ["pyproject.toml"],
  "bumpFiles": ["pyproject.toml"]
}
```

## Configuration

Configure via any of these (highest to lowest precedence):

1. CLI arguments
2. `.versionrc` / `.versionrc.json` (JSON)
3. `pyproject.toml` under `[tool.commit-and-tag-version]`
4. Built-in defaults

### Example `.versionrc.json`

```json
{
  "tagPrefix": "v",
  "packageFiles": ["pyproject.toml"],
  "bumpFiles": ["pyproject.toml"],
  "types": [
    {"type": "feat", "section": "Features"},
    {"type": "fix", "section": "Bug Fixes"},
    {"type": "refactor", "section": "Refactoring", "hidden": false}
  ],
  "releaseCommitMessageFormat": "chore(release): {{currentTag}}"
}
```

### Example `pyproject.toml`

```toml
[tool.commit-and-tag-version]
tag-prefix = "v"
package-files = ["pyproject.toml"]
bump-files = ["pyproject.toml"]
```

### Lifecycle Scripts

Execute custom commands at each stage of the release process:

```json
{
  "scripts": {
    "prerelease": "python -m pytest",
    "prebump": "echo 9.9.9",
    "postbump": "echo bumped!",
    "prechangelog": "",
    "postchangelog": "",
    "precommit": "",
    "postcommit": "",
    "pretag": "",
    "posttag": ""
  }
}
```

- `prebump`: If the script outputs a valid semver version, it overrides the calculated version.
- `precommit`: If the script outputs a string, it overrides the release commit message format.

### Customizing CHANGELOG Generation

Customize which commit types appear in the changelog and under what heading:

```json
{
  "types": [
    {"type": "feat", "section": "Features"},
    {"type": "fix", "section": "Bug Fixes"},
    {"type": "chore", "hidden": true},
    {"type": "docs", "hidden": true},
    {"type": "style", "hidden": true},
    {"type": "refactor", "section": "Refactoring", "hidden": false},
    {"type": "perf", "section": "Performance", "hidden": false},
    {"type": "test", "hidden": true}
  ]
}
```

## Code Usage

```python
from commit_and_tag_version import commit_and_tag_version
from commit_and_tag_version.defaults import get_default_config

config = get_default_config()
config.package_files = ["pyproject.toml"]
config.bump_files = ["pyproject.toml"]
config.dry_run = True

commit_and_tag_version(config)
```

## CLI Reference

```
Usage: commit-and-tag-version [OPTIONS]

Options:
  -r, --release-as TEXT           Specify release type or exact version
  -p, --prerelease TEXT           Make a prerelease with optional tag id
  -f, --first-release             Is this the first release?
  -s, --sign                      GPG sign commits and tags
  --signoff                       Add Signed-off-by trailer
  -n, --no-verify                 Bypass git hooks
  -a, --commit-all                Commit all staged changes
  --dry-run                       Simulate without making changes
  --silent                        Suppress output
  -t, --tag-prefix TEXT           Tag prefix (default: v)
  --tag-force                     Replace existing tag
  -c, --config PATH               Custom config file path
  -i, --infile TEXT               Changelog file path
  --release-count INTEGER         Number of releases in changelog
  --header TEXT                   Custom changelog header
  --release-commit-message-format TEXT
                                  Commit message format
  --commit-url-format TEXT        Commit URL format template
  --compare-url-format TEXT       Compare URL format template
  --issue-url-format TEXT         Issue URL format template
  --git-tag-fallback / --no-git-tag-fallback
                                  Fallback to git tags for version
  --path TEXT                     Only populate commits under this path
  --skip-bump                     Skip version bump
  --skip-changelog                Skip changelog generation
  --skip-commit                   Skip git commit
  --skip-tag                      Skip git tag
  --version                       Show the version and exit.
  --help                          Show this message and exit.
```

## FAQ

### How is this different from `python-semantic-release`?

`commit-and-tag-version` is **branch-agnostic** and **local-only**:

- No per-branch version strategies or branch-specific config
- No automatic pushing or publishing
- Deterministic bumps based solely on commit messages
- Prerelease is explicit via `--prerelease`, not inferred from branch names
- You control when and where to push

This makes it predictable across any git workflow — `feat:` always means minor, regardless of which branch you're on.

### Can I use this with non-Python projects?

Yes. Despite being written in Python, `commit-and-tag-version` supports version files for many ecosystems (Maven, Gradle, .NET, YAML, JSON, etc.). Install it as a global CLI tool and point it at your project's version file(s).

## License

MIT
