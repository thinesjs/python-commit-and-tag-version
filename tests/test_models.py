from commit_and_tag_version.models import Config, ParsedCommit, ScriptsConfig, SkipConfig


def test_skip_config_defaults():
    skip = SkipConfig()
    assert skip.bump is False
    assert skip.changelog is False
    assert skip.commit is False
    assert skip.tag is False


def test_scripts_config_defaults():
    scripts = ScriptsConfig()
    assert scripts.prebump is None
    assert scripts.postbump is None
    assert scripts.prerelease is None


def test_parsed_commit_creation():
    commit = ParsedCommit(
        type="feat",
        scope="cli",
        subject="add new option",
        body=None,
        breaking=False,
        breaking_note=None,
        references=[],
        raw="feat(cli): add new option",
    )
    assert commit.type == "feat"
    assert commit.scope == "cli"
    assert commit.breaking is False


def test_config_creation():
    config = Config(
        package_files=["package.json"],
        bump_files=["package.json"],
        infile="CHANGELOG.md",
        tag_prefix="v",
        preset="conventionalcommits",
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
        release_count=1,
        skip=SkipConfig(),
        scripts=ScriptsConfig(),
        header="# Changelog\n",
        commit_url_format=None,
        compare_url_format=None,
        issue_url_format=None,
        release_commit_message_format="chore(release): {{currentTag}}",
        git_tag_fallback=True,
        path=None,
        types=None,
    )
    assert config.tag_prefix == "v"
    assert config.skip.bump is False
