import sys

import click

from commit_and_tag_version import commit_and_tag_version
from commit_and_tag_version.config import load_config


@click.command(name="commit-and-tag-version")
@click.option(
    "--release-as", "-r", type=str, default=None, help="Specify release type or exact version"
)
@click.option(
    "--prerelease",
    "-p",
    type=str,
    default=None,
    is_flag=False,
    flag_value="",
    help="Make a prerelease with optional tag id",
)
@click.option(
    "--first-release", "-f", is_flag=True, default=False, help="Is this the first release?"
)
@click.option("--sign", "-s", is_flag=True, default=False, help="GPG sign commits and tags")
@click.option("--signoff", is_flag=True, default=False, help="Add Signed-off-by trailer")
@click.option("--no-verify", "-n", is_flag=True, default=False, help="Bypass git hooks")
@click.option("--commit-all", "-a", is_flag=True, default=False, help="Commit all staged changes")
@click.option("--dry-run", is_flag=True, default=False, help="Simulate without making changes")
@click.option("--silent", is_flag=True, default=False, help="Suppress output")
@click.option("--tag-prefix", "-t", type=str, default=None, help="Tag prefix (default: v)")
@click.option("--tag-force", is_flag=True, default=False, help="Replace existing tag")
@click.option("--config", "-c", type=click.Path(), default=None, help="Custom config file path")
@click.option("--infile", "-i", type=str, default=None, help="Changelog file path")
@click.option("--release-count", type=int, default=None, help="Number of releases in changelog")
@click.option("--header", type=str, default=None, help="Custom changelog header")
@click.option(
    "--release-commit-message-format", type=str, default=None, help="Commit message format"
)
@click.option("--commit-url-format", type=str, default=None, help="Commit URL format template")
@click.option("--compare-url-format", type=str, default=None, help="Compare URL format template")
@click.option("--issue-url-format", type=str, default=None, help="Issue URL format template")
@click.option(
    "--git-tag-fallback/--no-git-tag-fallback",
    default=None,
    help="Fallback to git tags for version",
)
@click.option("--path", type=str, default=None, help="Only populate commits under this path")
@click.option("--skip-bump", is_flag=True, default=False, help="Skip version bump")
@click.option("--skip-changelog", is_flag=True, default=False, help="Skip changelog generation")
@click.option("--skip-commit", is_flag=True, default=False, help="Skip git commit")
@click.option("--skip-tag", is_flag=True, default=False, help="Skip git tag")
@click.version_option()
def main(**kwargs):
    """Versioning using semver and CHANGELOG generation powered by Conventional Commits."""
    cli_args = {k: v for k, v in kwargs.items() if v is not None}

    skip_args = {}
    for skip_flag in ["skip_bump", "skip_changelog", "skip_commit", "skip_tag"]:
        val = cli_args.pop(skip_flag, None)
        if val:
            field = skip_flag.replace("skip_", "")
            skip_args[field] = True

    try:
        config = load_config(cli_args)

        if skip_args:
            for k, v in skip_args.items():
                setattr(config.skip, k, v)

        commit_and_tag_version(config)
    except Exception as err:
        if not kwargs.get("silent"):
            click.echo(f"Error: {err}", err=True)
        sys.exit(1)
