import re

VERSION_REGEX = re.compile(r"^version\s+=\s+['\"](\d[\d.]*)['\"]", re.MULTILINE)


class GradleUpdater:
    def read_version(self, contents: str) -> str:
        match = VERSION_REGEX.search(contents)
        if not match:
            raise ValueError(
                "Failed to read the version field in your gradle file - is it present?"
            )
        return match.group(1)

    def write_version(self, contents: str, version: str) -> str:
        return VERSION_REGEX.sub(f'version = "{version}"', contents)

    def is_private(self, contents: str) -> bool:
        return False
