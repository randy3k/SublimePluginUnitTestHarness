from sublime_unittest import *

class MyBufferTest(BufferTest):
    test_01_content = (
        "initial │content of buffer",
        "initial │content of buffer",
        )

    test_02_cursor = (
        "initial │content of buffer",
        v('move', {'by': 'characters', 'forward': False}),
        "initial│ content of buffer",
        )

    # here buffer is selected
    test_03_selection = (
        "initial content of ┤buffer├",
        v('insert', {'characters': "view"}),
        "initial content of view│",
    )

    # multiple cursors
    test_04_multiple_cursors = (
        "initial ┤content├ of bu│ffer",
        v('move', {'by': 'characters', 'forward': True}),
        "initial content│ of buf│fer",
        v('insert', {'characters': 'f'}),
        "initial contentf│ of buff│fer",
    )

    # line assertions, only selections, which are completely
    # contained in line are considered
    test_05_line_assertion = (
        unindent("""
        first ┤line
        second├ l│ine
        """),
        (2, "second├ l│ine")
    )
