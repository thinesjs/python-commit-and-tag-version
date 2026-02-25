from commit_and_tag_version.checkpoint import checkpoint
from commit_and_tag_version.format_commit_message import format_commit_message
from commit_and_tag_version.git import git_add, git_commit
from commit_and_tag_version.lifecycles.bump import get_updated_configs
from commit_and_tag_version.models import Config
from commit_and_tag_version.run_lifecycle_script import run_lifecycle_script


def commit(config: Config, new_version: str) -> None:
    if config.skip.commit:
        return

    hook_result = run_lifecycle_script(
        config.scripts, "precommit", silent=config.silent, dry_run=config.dry_run
    )
    if hook_result:
        config.release_commit_message_format = hook_result

    updated = get_updated_configs()
    files_to_add: list[str] = []

    if not config.skip.changelog:
        files_to_add.append(config.infile)

    for filename in updated:
        if filename not in files_to_add:
            files_to_add.append(filename)

    msg = format_commit_message(config.release_commit_message_format, new_version)

    checkpoint("committing %s", [config.infile], silent=config.silent, dry_run=config.dry_run)

    git_add(files_to_add, dry_run=config.dry_run)
    git_commit(
        message=msg,
        sign=config.sign,
        signoff=config.signoff,
        no_verify=config.no_verify,
        dry_run=config.dry_run,
        files=files_to_add if not config.commit_all else None,
    )

    run_lifecycle_script(config.scripts, "postcommit", silent=config.silent, dry_run=config.dry_run)
