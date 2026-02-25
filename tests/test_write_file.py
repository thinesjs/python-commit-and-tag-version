from commit_and_tag_version.write_file import write_file


def test_writes_content_to_file(tmp_path):
    file_path = tmp_path / "test.txt"
    write_file(file_path, "hello world", dry_run=False)
    assert file_path.read_text() == "hello world"


def test_dry_run_does_not_write(tmp_path):
    file_path = tmp_path / "test.txt"
    write_file(file_path, "hello world", dry_run=True)
    assert not file_path.exists()
