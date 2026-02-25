import json


def _detect_indent(text: str) -> str:
    for line in text.split("\n"):
        stripped = line.lstrip()
        if stripped and line != stripped:
            return line[: len(line) - len(stripped)]
    return "  "


def _detect_newline(text: str) -> str:
    if "\r\n" in text:
        return "\r\n"
    return "\n"


def _stringify_package(data: dict, indent: str, newline: str) -> str:
    indent_size = len(indent)
    if indent_size == 0:
        indent_size = 2
    result = json.dumps(data, indent=indent_size, ensure_ascii=False)
    if newline == "\r\n":
        result = result.replace("\n", "\r\n") + "\r\n"
    else:
        result = result + "\n"
    return result


class JsonUpdater:
    def read_version(self, contents: str) -> str:
        return json.loads(contents)["version"]

    def write_version(self, contents: str, version: str) -> str:
        data = json.loads(contents)
        indent = _detect_indent(contents)
        newline = _detect_newline(contents)
        data["version"] = version
        if "packages" in data and "" in data["packages"]:
            data["packages"][""]["version"] = version
        return _stringify_package(data, indent, newline)

    def is_private(self, contents: str) -> bool:
        return bool(json.loads(contents).get("private", False))
