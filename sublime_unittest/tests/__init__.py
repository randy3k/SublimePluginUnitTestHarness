from imp import reload

# make sure newest version of test_main is loaded
from . import test_main, test_buffer
reload(test_main)
reload(test_buffer)

# here you also could reload modules under test

# load testcases

from .test_main import *
from .test_buffer import *