import unittest, sys, re

class DeferrableTestCase(unittest.TestCase):

    def run(self, result=None):
        from unittest.case import _ExpectedFailure, _UnexpectedSuccess, SkipTest

        orig_result = result
        if result is None:
            result = self.defaultTestResult()
            startTestRun = getattr(result, 'startTestRun', None)
            if startTestRun is not None:
                startTestRun()

        self._resultForDoCleanups = result
        result.startTest(self)

        testMethod = getattr(self, self._testMethodName)
        if (getattr(self.__class__, "__unittest_skip__", False) or
            getattr(testMethod, "__unittest_skip__", False)):
            # If the class or method was skipped.
            try:
                skip_why = (getattr(self.__class__, '__unittest_skip_why__', '')
                            or getattr(testMethod, '__unittest_skip_why__', ''))
                self._addSkip(result, skip_why)
            finally:
                result.stopTest(self)
            return
        try:
            success = False
            try:
                deferred = self.setUp()
                if deferred is not None:
                    for x in deferred: yield x
            except SkipTest as e:
                self._addSkip(result, str(e))
            except KeyboardInterrupt:
                raise
            except:
                result.addError(self, sys.exc_info())
            else:
                try:
                    deferred = testMethod()
                    if deferred is not None:
                    	for x in deferred: yield x
                except KeyboardInterrupt:
                    raise
                except self.failureException:
                    result.addFailure(self, sys.exc_info())
                except _ExpectedFailure as e:
                    addExpectedFailure = getattr(result, 'addExpectedFailure', None)
                    if addExpectedFailure is not None:
                        addExpectedFailure(self, e.exc_info)
                    else:
                        warnings.warn("TestResult has no addExpectedFailure method, reporting as passes",
                                      RuntimeWarning)
                        result.addSuccess(self)
                except _UnexpectedSuccess:
                    addUnexpectedSuccess = getattr(result, 'addUnexpectedSuccess', None)
                    if addUnexpectedSuccess is not None:
                        addUnexpectedSuccess(self)
                    else:
                        warnings.warn("TestResult has no addUnexpectedSuccess method, reporting as failures",
                                      RuntimeWarning)
                        result.addFailure(self, sys.exc_info())
                except SkipTest as e:
                    self._addSkip(result, str(e))
                except:
                    result.addError(self, sys.exc_info())
                else:
                    success = True

                try:
                    deferred = self.tearDown()
                    if deferred is not None:
                        for x in deferred: yield x
                except KeyboardInterrupt:
                    raise
                except:
                    result.addError(self, sys.exc_info())
                    success = False

            cleanUpSuccess = self.doCleanups()
            success = success and cleanUpSuccess
            if success:
                result.addSuccess(self)
        finally:
            result.stopTest(self)
            if orig_result is None:
                stopTestRun = getattr(result, 'stopTestRun', None)
                if stopTestRun is not None:
                    stopTestRun()

class sublime_command:
    def __init__(self, command, args):
        self.cmd  = command
        self.args = args

class v(sublime_command):
    def __call__(self, buffer_test):
        buffer_test.view.run_command(self.cmd, self.args)

class w(sublime_command):
    def __call__(self, buffer_test):
        buffer_test.view.window().run_command(self.cmd, self.args)

INDENT_RE = re.compile('^[\x20\t]*')
def unindent(s):
    if s.startswith('\n'): s = s[1:]
    ind = INDENT_RE.match(s).group(0)
    il = len(ind)
    output = []
    for l in s.splitlines(1):
        if l.startswith(ind):
            output.append(l[il:])
        else:
            output.append(l)
    return ''.join(output)

uni = unindent

# from six.py
def add_metaclass(metaclass):
    """Class decorator for creating a class with a metaclass."""
    def wrapper(cls):
        orig_vars = cls.__dict__.copy()
        orig_vars.pop('__dict__', None)
        orig_vars.pop('__weakref__', None)
        for slots_var in orig_vars.get('__slots__', ()):
            orig_vars.pop(slots_var)
        return metaclass(cls.__name__, cls.__bases__, orig_vars)
    return wrapper

class TestDataClass(type):
    def __init__(cls, name, bases, nmspc):
        super(TestDataClass, cls).__init__(name, bases, nmspc)

        def make_method(args):
            return lambda self: self.simple_test(*args)

        for name in dir(cls):
            if not name.startswith('test'): continue
            v = getattr(cls, name)
            if isinstance(v, (tuple, list)):
                setattr(cls, name, make_method(v))


@add_metaclass(TestDataClass)
class BufferTest(DeferrableTestCase):
    testfile = None
    def setUp(self):
        if not self.testfile:
            self.testfile = "BufferTest"
        import sublime
        self.view = sublime.active_window().open_file(self.testfile)
        self.view.set_scratch(True)

    def tearDown(self):
        self.view.window().run_command('close', {})

    def begin_edit(self):
        from .edit import Edit
        self.edit = Edit(self.view)

    def set_sel(self, *regions):
        import sublime
        self.view.sel().clear()
        for r in regions:
            assert isinstance(r, (sublime.Region, int)), ""
            self.view.sel().add(r)
        #self.view.sel().add_all(regions)

    def is_done_editing(self):
        return not self.editing

    def done_editing(self):
        self.editing = False

    def content(self, content=None):
        from .edit import Edit
        import sublime
        if content is None:
            return self.view.substr(sublime.Region(0, self.view.size()))
        else:
            self.editing = True
            with Edit(self.view) as edit:
                edit.replace(sublime.Region(0, self.view.size()), content)
                edit.callback(lambda:self.set_sel(self.view.size()))
                edit.callback(self.done_editing)

            return self.is_done_editing

    def encode_sel(self):
        content = self.content()
        #output = [ content[0:self.view.sel()[0].begin()]]
        output = []
        a = 0
        sel = None
        for sel in self.view.sel():
            output.append(content[a:sel.begin()])

            if sel.begin() == sel.end():
                output.append('│') # ctrl+k,v,v
            else:
                output.append('┤') # ctrl+k,v,l,space
                output.append(self.view.substr(sel))
                output.append('├') # ctrl+k,v,r

            a = sel.end()

        if not a:
            output.append( content )

        if a:
            output.append( content[a:])

        return ''.join(output)

    def decode_sel(self, content):
        import sublime
        input = re.split(r'([│┤├])', content)
        content = ''
        pos = 0
        sel = []
        for s in input:
            if s == '│':
                sel.append( pos )
            elif s == '├':
                sel.append( sublime.Region(a, pos) )
            elif s == '┤':
                a = pos
            else:
                pos += len(s)
                content += s

        return content, sel

    def simple_test(self, *test_data):
        yield lambda: not self.view.is_loading()

        content, sel = self.decode_sel(test_data[0])
        yield self.content(content)
        self.set_sel(*sel)

        #import spdb ; spdb.start()
        for a in test_data[1:]:
            if isinstance(a, sublime_command):
                yield a(self)

            if isinstance(a, str):
                content = self.encode_sel()
                self.assertEquals(content, a)

                # content, sels = self.decode_sel(a)
                # self.assertEquals(self.content(), content)
                # for i,sel in enumerate(self.view.sel()):
                #     if sel.begin() == sel.end():
                #         sel = sel.end()
                #     self.assertEquals(sels[i], sel)

            if isinstance(a, tuple):
                content = self.encode_sel()
                lineno, line = a
                self.assertEquals(content.splitlines()[lineno-1], line)

                # p = self.view.text_point(lineno, 0)
                # line, sels = self.decode_sel(line)
                # line_region = self.view.line(p)

                # _sels = []
                # for sel in self.view.sel():
                #     if line_region.contains(sel):
                #         _sels.append(sel)

                # self.assertEquals(line, self.view.substr(line_region))

                # for i,sel in enumerate(sels):
                #     r = sels[i]
                #     self.assertEquals( 
                #         (p+r.begin(), p+r.end()), 
                #         (sel.begin(), sel.end())
                #         )