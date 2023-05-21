from typing import Callable

def _print(*a):
    print(*a)


def open_file(path):
    return open(path)


FUNCTIONS: dict[str, Callable] = {
    "print": _print,
    "write_file": open_file,
}

INVERTED_FUNCTIONS: dict[Callable, str] = {v: k for k, v in FUNCTIONS.items()}
