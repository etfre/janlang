def _print(*a):
    print(*a)


def open_file(path):
    return open(path)


FUNCTIONS = {
    "print": _print,
    "write_file": open_file,
}
