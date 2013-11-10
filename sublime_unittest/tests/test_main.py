import sublime, sublime_plugin
import time, os, sys

import pprint
pprint.pprint([x for x in sorted(sys.modules)])
from sublime_unittest import TestCase

PLUGIN_NAME = 'Plugin UnitTest Harness'

ST3 = sublime.version() >= '3000'

def view_close(view):
	if ST3:
		view.close()
	else:
		raise NotImplementedError

def load_resource(name):
	if ST3:
		return sublime.load_resource(name)
	else:
		name = os.path.join(sublime.packages_path(), '..', name)
		with open(name, r) as f:
			return f.read()

def get_cache_dir(*name):
	try:
		p = os.path.join(sublime.cache_path(), PLUGIN_NAME, *name)
	except:
		p = os.path.normpath(os.path.join(sublime.packages_path(), '..', PLUGIN_NAME, *name))

	if not os.path.exists(p):
		os.makedirs(p)

	return p

def deployed_cache_file(filename):
	p = get_cache_dir()

	src = load_resource('Packages/%s/%s' % (PLUGIN_NAME, filename))

	cache_file_name = os.path.join(p, filename)
	dirname = os.path.dirname(cache_file_name)

	if not os.path.exists(dirname):
		os.makedirs(dirname)

	if not os.path.exists(cache_file_name):
		with open(cache_file_name, 'w') as f:
			f.write(src)

	return cache_file_name


class PluginUnitTestExamplTest(TestCase):

	def setUp(self):
		#import spdb ; spdb.start()
		
		testfile = deployed_cache_file('sublime_unittest/tests/__init__.py')
		self.view = sublime.active_window().open_file(testfile)


	def tearDown(self):
		view_close(self.view)

	def test_shall_succeed(self):
		r'''This makes some tests of sublime API to get or set scope_names

		'''

		while self.view.is_loading():
			yield

		self.assertEquals( self.view.extract_scope(100), sublime.Region(98, 105))

		yield

		self.assertEquals(self.view.scope_name(100), 
			"source.python meta.function-call.python "
			"support.function.builtin.python ")

		self.assertEquals(self.view.find_by_selector('comment'), 

			[ sublime.Region(*x) for x in 
				[ (24, 74), (117, 165), (166, 183) 
				  ]
			])

	def test_shall_fail(self):

		while self.view.is_loading():
			yield

		my_regions = [ sublime.Region(*x) for x in [(472, 504), (536, 568)] ]

		self.view.add_regions("my_regions", my_regions, 'entity.name.tag.restructuredtext', '', sublime.HIDDEN) 

		yield

		self.assertEquals(self.view.get_regions("my_regions"), my_regions)

		self.assertEquals(self.view.scope_name(500), 'some wrong expectation')
