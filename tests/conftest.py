import json
import subprocess

import pytest


@pytest.fixture
def git_repo(tmp_path):
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=tmp_path,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=tmp_path,
        capture_output=True,
        check=True,
    )
    (tmp_path / ".gitkeep").write_text("")
    subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True, check=True)
    subprocess.run(
        ["git", "commit", "-m", "chore: initial commit"],
        cwd=tmp_path,
        capture_output=True,
        check=True,
    )
    return tmp_path


@pytest.fixture
def git_repo_with_package(git_repo):
    pkg = {"name": "test", "version": "1.0.0"}
    (git_repo / "package.json").write_text(json.dumps(pkg, indent=2) + "\n")
    subprocess.run(["git", "add", "package.json"], cwd=git_repo, capture_output=True, check=True)
    subprocess.run(
        ["git", "commit", "-m", "chore: add package.json"],
        cwd=git_repo,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "tag", "-a", "v1.0.0", "-m", "chore(release): 1.0.0"],
        cwd=git_repo,
        capture_output=True,
        check=True,
    )
    return git_repo
