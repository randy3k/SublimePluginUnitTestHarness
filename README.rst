Plugin UnitTest Harness
=======================

This plugin provides deferred testcases, such you are able to run sublime
commands from your test cases and give control to sublime text and get it back
later.

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


Todo
====

- have some ``TestCase.sendkeys()`` method to send keys after opening a panel


