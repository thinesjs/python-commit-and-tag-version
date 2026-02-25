class PlainTextUpdater:
    def read_version(self, contents: str) -> str:
        return contents.strip()

    def write_version(self, contents: str, version: str) -> str:
        return version

    def is_private(self, contents: str) -> bool:
        return False
