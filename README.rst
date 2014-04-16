Plugin UnitTest Harness
=======================

This plugin provides deferred testcases, such you are able to run sublime
commands from your test cases and give control to sublime text and get 
it back later.

Usage
-----

Create a folder for your tests.  If you want to stay sublime text 2 compatible
you should not call it "tests" in your main plugin folder, because of name clashes.

Following layout is recommended:

    - My Fancy Plugin
      - my_fancy_plugin
        - __init__.py
        - some_file.py
        - tests
          - __init__.py
          - test_first_collection.py
          - test_second_collection.py
      - My Fancy Plugin.py
      - My Fancy Plugin.sublime-commands

My Fancy Plugin.py
    ... is your major plugin file, which is automatically reloaded by
    Sublime Text on change.  The other python files within subfolders are not. This 
    contains your commands you export to sublime text or whatever.

My Fancy Plugin.sublime-commands
    This has to contain a command to start your tests::
        [
            { "caption": "My Fancy Plugin: Run Tests", 
              "command": "run_plugin_unittest", 
              "args": {"module": "My Fancy Plugin.my_fancy_plugin.tests"} }
        ]

my_fancy_plugin/tests/__init__.py
    On each test the module passed to ``run_plugin_unittest`` is reloaded. 
    So this file is responsible to reload everything, which is needed for the 
    test::

        # this is the class, which is run by run_plugin_unittest

        from imp import reload

        # make sure we have got latest changes

        from . import test_first_collection
        reload(test_first_collection)

        from . import test_second_collection
        reload(test_second_collection)

        from .. import some_file
        reload(some_file)

        # import all testcases
        from .test_first_collection import *
        from .test_second_collection import *


my_fancy_plugin/tests/test_first_collection.py
    This contains testcases::

        from sublime_unittest import TestCase
        import sublime

        class MyTest(TestCase):

            def test_first(self):
                view = sublime.active_window().open_file("some file")

                while view.is_loading():
                    yield     # default is to continue in 10ms

                self.assertEquals(view.name(), "some file")

            def test_second(self):
                view = sublime.active_window().open_file("some file")

                while view.is_loading():
                    yield 2   # I specify that sublime shall continue this code in 2ms

                self.assertEquals(view.file_name(), "some file")

                
and so on ...


Simple Buffer Tests
-------------------

You can create simple buffer tests like this::

    from sublime_unittest import *

    class MyBufferTest(BufferTest):
        test_cursor = (
            "initial │content of buffer",
            v('move', {'by': 'characters', 'forward': False}),
            "initial│ content of buffer",
            )

        # here buffer is selected
        test_selection = (
            "initial content of ┤buffer├",
            v('insert', {'characters': "view"}),
            "initial content of view│",
        )

        # multiple cursors
        test_multiple_cursors = (
            "initial ┤content├ of bu│ffer",
            v('move', {'by': 'characters', 'forward': True}),
            "initial content │of buf│fer",
            v('insert', {'characters': 'f'}),
            "initial content f│of buff│fer",
        )

        # line assertions
        test_line_assertion = (
            unindent("""
            first ┤line
            second├ l│ine
            """),
            (2, "second├ l│ine")
        )

- all test names have to start with 'test'

- You specify a text command (or view command) with ``v`` and a window
  command with ``w``.

- Each string means an assertion.

- You can mix commands and assertions however you like.

- ``┤`` and ``├`` encloses a selection and ``│`` is an empty selection, 
  i.e. a cursor.  

  .. note:: 

     Using `Character Table`_ Plugin you can shortcut these characters with
     ``ctrl+k,v,l``, ``ctrl+k,v,r`` and ``ctrl+k,v,v``

.. _Character Table: https://sublime.wbond.net/packages/Character%20Table


Todo
----

- have some ``TestCase.sendkeys()`` method to send keys after opening a panel


Changes
-------

2014-04-16
    - added BufferTest for convenient buffer tests
    - added opportunity to yield a method to wait for some condition 
      before continuing test


Author
------

Kay-Uwe (Kiwi) Lorenz <kiwi@franka.dyndns.org> (http://quelltexter.org)

Support my work on `Sublime Text Plugins`_: `Donate via Paypal`_

.. _Sublime Text Plugins:
    https://sublime.wbond.net/browse/authors/Kay-Uwe%20%28Kiwi%29%20Lorenz%20%28klorenz%29
    
.. _Donate via Paypal:
    https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WYGR49LEGL9C8