from commit_and_tag_version.format_commit_message import format_commit_message


def test_replaces_current_tag():
    result = format_commit_message("chore(release): {{currentTag}}", "1.2.3")
    assert result == "chore(release): 1.2.3"


def test_replaces_multiple_occurrences():
    result = format_commit_message("v{{currentTag}} release {{currentTag}}", "2.0.0")
    assert result == "v2.0.0 release 2.0.0"


def test_no_replacement_needed():
    result = format_commit_message("static message", "1.0.0")
    assert result == "static message"
