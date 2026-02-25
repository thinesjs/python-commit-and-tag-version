import re

VERSION_REGEX = re.compile(r"<Version>(.*)</Version>")


class CsprojUpdater:
    def read_version(self, contents: str) -> str:
        match = VERSION_REGEX.search(contents)
        if not match:
            raise ValueError(
                "Failed to read the Version field in your csproj file - is it present?"
            )
        return match.group(1)

    def write_version(self, contents: str, version: str) -> str:
        return VERSION_REGEX.sub(f"<Version>{version}</Version>", contents)

    def is_private(self, contents: str) -> bool:
        return False
