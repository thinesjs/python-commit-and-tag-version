import subprocess

from commit_and_tag_version.checkpoint import checkpoint
from commit_and_tag_version.models import ScriptsConfig


def run_lifecycle_script(
    scripts: ScriptsConfig,
    hook_name: str,
    silent: bool = False,
    dry_run: bool = False,
) -> str | None:
    command = getattr(scripts, hook_name, None)
    if not command:
        return None

    checkpoint('Running lifecycle script "%s"', [hook_name], silent=silent)
    checkpoint('- execute command: "%s"', [command], silent=silent)

    if dry_run:
        return None

    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip() if result.stdout else None
