import re
import xml.etree.ElementTree as ET


class MavenUpdater:
    def read_version(self, contents: str) -> str:
        root = ET.fromstring(contents)
        version_elem = root.find("version")
        if version_elem is None or version_elem.text is None:
            raise ValueError("Failed to read the version field in your pom file - is it present?")
        return version_elem.text

    def write_version(self, contents: str, version: str) -> str:
        pattern = re.compile(r"(<version>)(.*?)(</version>)", re.DOTALL)
        matches = list(pattern.finditer(contents))
        if not matches:
            raise ValueError("Failed to read the version field in your pom file")
        for m in matches:
            preceding = contents[: m.start()]
            if "<parent>" in preceding and "</parent>" not in preceding:
                continue
            if "<dependency>" in preceding:
                last_dep_close = preceding.rfind("</dependency>")
                last_dep_open = preceding.rfind("<dependency>")
                if last_dep_open > last_dep_close:
                    continue
            if "<properties>" in preceding:
                last_prop_close = preceding.rfind("</properties>")
                last_prop_open = preceding.rfind("<properties>")
                if last_prop_open > last_prop_close:
                    continue
            return contents[: m.start(2)] + version + contents[m.end(2) :]
        raise ValueError("Failed to find project version in pom file")

    def is_private(self, contents: str) -> bool:
        return False
