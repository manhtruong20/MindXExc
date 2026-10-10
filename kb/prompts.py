import sys
from pathlib import Path

def ask_valid(field, value, prompt, check):
    """Return check(value), asking again until the value is valid.

    If value is None the user is asked for it. When check raises ValueError,
    the reason is printed to stderr and the user is asked again, the same
    behaviour as `tickets create`.
    """
    while True:
        if value is None:
            value = input(prompt)
        try:
            return check(value)
        except ValueError as error:
            print(f"Invalid {field}: {error}", file=sys.stderr)
            value = None


def read_text_file(value):
    if not value.strip():
        raise ValueError("must not be empty")
    path = Path(value)
    try:
        return path, path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise ValueError(f"cannot read {value}: {error}")


def check_node_path(value):
    if not value.strip():
        raise ValueError("must not be empty")
    return value


def check_tags(value):
    tags = value.split()
    for tag in tags:
        if tag.startswith("-"):
            raise ValueError(f"tag {tag!r} must not start with '-'")
    return list(dict.fromkeys(tags))