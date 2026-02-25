import sys


def checkpoint(msg: str, args: list[str], silent: bool = False, dry_run: bool = False) -> None:
    if silent:
        return
    figure = "\u2713" if not dry_run else "\u2299"
    formatted_args = [f"\033[1m{a}\033[0m" for a in args]
    formatted_msg = msg
    for arg in formatted_args:
        formatted_msg = formatted_msg.replace("%s", arg, 1)
    print(f"  {figure} {formatted_msg}", file=sys.stderr)


def print_error(msg: str, silent: bool = False) -> None:
    if silent:
        return
    print(f"\033[31m{msg}\033[0m", file=sys.stderr)
