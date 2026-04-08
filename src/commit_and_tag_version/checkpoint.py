import os
import sys


def _supports_color() -> bool:
    if "NO_COLOR" in os.environ:
        return False
    if "FORCE_COLOR" in os.environ:
        return True
    return sys.stderr.isatty()


def _bold(value: str) -> str:
    return f"\033[1m{value}\033[0m" if _supports_color() else value


def _red(value: str) -> str:
    return f"\033[31m{value}\033[0m" if _supports_color() else value


def checkpoint(msg: str, args: list[str], silent: bool = False, dry_run: bool = False) -> None:
    if silent:
        return
    figure = "\u2713" if not dry_run else "\u2299"
    formatted_args = [_bold(a) for a in args]
    formatted_msg = msg
    for arg in formatted_args:
        formatted_msg = formatted_msg.replace("%s", arg, 1)
    print(f"  {figure} {formatted_msg}", file=sys.stderr)


def print_error(msg: str, silent: bool = False) -> None:
    if silent:
        return
    print(_red(msg), file=sys.stderr)
