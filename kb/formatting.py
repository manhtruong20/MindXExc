import textwrap

PREVIEW_WIDTH = 80
PREVIEW_LINES = 3
def preview(text, width=PREVIEW_WIDTH, max_lines=PREVIEW_LINES):
    """Return a short preview of ``text`` for terminal output.

    Every line is wrapped at ``width`` characters. Only the first
    ``max_lines`` displayed lines are kept (wrapped lines count towards the
    limit), and a final "..." line is added when something was cut off.
    Blank lines are kept.
    """
    lines = []
    for line in text.splitlines():
        lines.extend(textwrap.wrap(line, width) or [""])
    shown = lines[:max_lines]
    if len(lines) > max_lines:
        shown.append("...")
    return "\n".join(shown)