def format_commit_message(raw_msg: str, new_version: str) -> str:
    return str(raw_msg).replace("{{currentTag}}", new_version)
