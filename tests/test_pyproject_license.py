from pathlib import Path


def test_license_is_mit():
    pyproject = Path(__file__).parent.parent / "pyproject.toml"
    content = pyproject.read_text(encoding="utf-8")
    assert 'license = "MIT"' in content
