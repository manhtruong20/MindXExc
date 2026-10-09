import textwrap

def preview(text, width=80, max_lines=3):
    lines = []
    for line in text.splitlines():
        lines.extend(textwrap.wrap(line, width) or [""])
    shown = lines[:max_lines]
    if len(lines) > max_lines:
        shown.append("...")
    return "\n".join(shown)