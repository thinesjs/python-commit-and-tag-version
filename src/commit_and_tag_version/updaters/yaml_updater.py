import yaml


class YamlUpdater:
    def read_version(self, contents: str) -> str:
        data = yaml.safe_load(contents)
        return str(data["version"])

    def write_version(self, contents: str, version: str) -> str:
        newline = "\r\n" if "\r\n" in contents else "\n"
        data = yaml.safe_load(contents)
        data["version"] = version
        result = yaml.dump(data, default_flow_style=False, sort_keys=False)
        if newline == "\r\n":
            result = result.replace("\n", "\r\n")
        return result

    def is_private(self, contents: str) -> bool:
        return False
