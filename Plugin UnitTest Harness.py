from unittest import loader
import sublime, sublime_plugin
from .sublime_unittest import DeferrableSuite, DeferringTextTestRunner

ST3 = sublime.version() >= '3000'

class OutputPanel:
    r'''create an output panel and mimic an output stream for writing'''

    def __init__(self, name, file_regex='', line_regex = '', 
        base_dir = None, word_wrap = False, line_numbers = False, 
        gutter = False, scroll_past_end = False, 
        syntax = 'Packages/Text/Plain text.tmLanguage'):

        self.name = name

        self.window = sublime.active_window()

        # Try not to call get_output_panel until the regexes are assigned
        self.output_view = self.window.create_output_panel(name)

        # Default the to the current files directory if no working directory was given
        if (base_dir == "" and self.window.active_view()
                        and self.window.active_view().file_name()):
            base_dir = os.path.dirname(self.window.active_view().file_name())

        self.output_view.settings().set("result_file_regex", file_regex)
        self.output_view.settings().set("result_line_regex", line_regex)
        self.output_view.settings().set("result_base_dir", base_dir)
        self.output_view.settings().set("word_wrap", word_wrap)
        self.output_view.settings().set("line_numbers", line_numbers)
        self.output_view.settings().set("gutter", gutter)
        self.output_view.settings().set("scroll_past_end", scroll_past_end)
        self.output_view.assign_syntax(syntax)

    def write(self, s):
        self.output_view.run_command('append', {'characters': s, 
            'force': True, 'scroll_to_end': True})

    def flush(self):
        pass

    def writeln(self, s):
        self.write(s)
        self.write("\n")

    def show(self):
        self.window.run_command("show_panel", {"panel": "output."+self.name})

class RunPluginUnittestCommand(sublime_plugin.WindowCommand):

    def run(self, module):
        import importlib
        module = importlib.import_module(module)   #'Syntax Highlight Extension.syntax_highlight_tests')

        #import spdb ; spdb.start()

        from imp import reload

        # make sure the module under test is up to date
        reload(module)

        test = loader.findTestCases(module, suiteClass=DeferrableSuite)

        output_panel = OutputPanel('unittests', 
            file_regex = r'File "([^"]*)", line (\d+)'
            )
        output_panel.show()

        testRunner = DeferringTextTestRunner(stream=output_panel)
        testRunner.run(test)

def plugin_loaded():
    from . import sublime_unittest
    import sys
    sys.stderr.write("sublime_unittest: %s\n" % sublime_unittest)
    sys.modules['sublime_unittest'] = sublime_unittest

def plugin_unloaded():
    import sys
    del sys.modules['sublime_unittest']

if not ST3:
    plugin_loaded()

    def unload_handler():
        plugin_unloaded()
