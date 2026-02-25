import re

VERSION_REGEX = re.compile(r'version[" ]*=[ ]*["\'](.*)["\']', re.IGNORECASE)


class PythonUpdater:
    def read_version(self, contents: str) -> str:
        for line in contents.split("\n"):
            match = VERSION_REGEX.match(line.strip())
            if match:
                return match.group(1)
        raise ValueError("Failed to read version from pyproject.toml")

    def write_version(self, contents: str, version: str) -> str:
        lines = contents.split("\n")
        for i, line in enumerate(lines):
            match = VERSION_REGEX.match(line.strip())
            if match:
                old_version = match.group(1)
                lines[i] = line.replace(old_version, version)
                break
        return "\n".join(lines)

    def is_private(self, contents: str) -> bool:
        return False
