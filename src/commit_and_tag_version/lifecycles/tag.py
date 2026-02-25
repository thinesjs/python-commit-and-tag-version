import sys

from commit_and_tag_version.checkpoint import checkpoint
from commit_and_tag_version.format_commit_message import format_commit_message
from commit_and_tag_version.git import get_current_branch, git_tag
from commit_and_tag_version.models import Config
from commit_and_tag_version.run_lifecycle_script import run_lifecycle_script


def tag(new_version: str, pkg_private: bool, config: Config) -> None:
    if config.skip.tag:
        return

    run_lifecycle_script(config.scripts, "pretag", silent=config.silent, dry_run=config.dry_run)

    tag_name = f"{config.tag_prefix}{new_version}"
    msg = format_commit_message(config.release_commit_message_format, new_version)

    checkpoint("tagging release %s", [tag_name], silent=config.silent, dry_run=config.dry_run)

    git_tag(
        name=tag_name,
        message=msg,
        sign=config.sign,
        force=config.tag_force,
        dry_run=config.dry_run,
    )

    run_lifecycle_script(config.scripts, "posttag", silent=config.silent, dry_run=config.dry_run)

    if not pkg_private and not config.silent:
        branch = get_current_branch()
        print(
            f"\nRun `git push --follow-tags origin {branch}` to publish",
            file=sys.stderr,
        )
