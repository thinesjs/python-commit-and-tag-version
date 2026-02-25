from commit_and_tag_version.commit_parser import parse_commit, recommend_bump


class TestParseCommit:
    def test_simple_feat(self):
        result = parse_commit("feat: add new feature")
        assert result.type == "feat"
        assert result.scope is None
        assert result.subject == "add new feature"
        assert result.breaking is False

    def test_feat_with_scope(self):
        result = parse_commit("feat(cli): add option")
        assert result.type == "feat"
        assert result.scope == "cli"
        assert result.subject == "add option"

    def test_fix(self):
        result = parse_commit("fix: resolve crash")
        assert result.type == "fix"
        assert result.subject == "resolve crash"

    def test_breaking_with_exclamation(self):
        result = parse_commit("feat!: breaking change")
        assert result.breaking is True

    def test_breaking_with_scope_and_exclamation(self):
        result = parse_commit("refactor(core)!: rewrite internals")
        assert result.breaking is True
        assert result.scope == "core"

    def test_breaking_change_footer(self):
        msg = "feat: something\n\nBREAKING CHANGE: removed old API"
        result = parse_commit(msg)
        assert result.breaking is True
        assert result.breaking_note == "removed old API"

    def test_breaking_change_footer_hyphenated(self):
        msg = "feat: something\n\nBREAKING-CHANGE: removed old API"
        result = parse_commit(msg)
        assert result.breaking is True

    def test_issue_references(self):
        result = parse_commit("fix: resolve crash (#123)")
        assert "#123" in result.references

    def test_closes_reference(self):
        msg = "fix: bug\n\nCloses #456"
        result = parse_commit(msg)
        assert "#456" in result.references

    def test_non_conventional_commit_returns_none(self):
        result = parse_commit("just a regular message")
        assert result is None

    def test_body_parsing(self):
        msg = "feat: title\n\nThis is the body\nwith multiple lines"
        result = parse_commit(msg)
        assert result.body == "This is the body\nwith multiple lines"

    def test_chore_type(self):
        result = parse_commit("chore: update deps")
        assert result.type == "chore"


class TestRecommendBump:
    def test_no_commits_returns_patch(self):
        assert recommend_bump([]) == "patch"

    def test_fix_returns_patch(self):
        commits = [parse_commit("fix: bug")]
        assert recommend_bump(commits) == "patch"

    def test_feat_returns_minor(self):
        commits = [parse_commit("feat: feature")]
        assert recommend_bump(commits) == "minor"

    def test_breaking_returns_major(self):
        commits = [parse_commit("feat!: breaking")]
        assert recommend_bump(commits) == "major"

    def test_breaking_before_1_0_0_returns_minor(self):
        commits = [parse_commit("feat!: breaking")]
        assert recommend_bump(commits, current_version="0.5.0") == "minor"

    def test_mixed_commits_highest_wins(self):
        commits = [
            parse_commit("fix: bug"),
            parse_commit("feat: feature"),
            parse_commit("chore: cleanup"),
        ]
        assert recommend_bump(commits) == "minor"

    def test_breaking_footer_returns_major(self):
        commits = [parse_commit("feat: x\n\nBREAKING CHANGE: removed API")]
        assert recommend_bump(commits) == "major"
