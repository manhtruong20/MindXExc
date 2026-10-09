from kb.formatting import preview


def test_short_text_is_unchanged():
    assert preview("one\ntwo") == "one\ntwo"


def test_only_the_first_three_lines_are_kept():
    assert preview("1\n2\n3\n4\n5") == "1\n2\n3\n..."


def test_long_lines_are_wrapped_at_the_width():
    assert preview("aaaa bbbb cccc", width=9) == "aaaa bbbb\ncccc"


def test_wrapped_lines_count_towards_the_limit():
    text = "aaaa bbbb cccc dddd"

    assert preview(text, width=4, max_lines=3) == "aaaa\nbbbb\ncccc\n..."


def test_blank_lines_are_kept():
    assert preview("a\n\nb") == "a\n\nb"


def test_empty_text_gives_empty_string():
    assert preview("") == ""