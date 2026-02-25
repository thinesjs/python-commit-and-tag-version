from pathlib import Path


def write_file(file_path: str | Path, content: str, dry_run: bool = False) -> None:
    if dry_run:
        return
    Path(file_path).write_text(content, encoding="utf-8")
