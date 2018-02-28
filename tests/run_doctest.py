"""
Testing
"""

import doctest, unittest, sys


# import all of the modules that need testing
import unittest

# build a list of all modules that contain doctests
test_modules = [
    'easier68k.core.util.conversions'
]

def load_tests(tests):
    """
    Loads each of the tests contained in the modules
    :param tests:
    :return:
    """
    for mod in test_modules:
        tests.addTests(doctest.DocTestSuite(mod))
    return tests

if __name__ == '__main__':
    """
    Evaluate all of the tests that were loaded.
    """

    tests = unittest.TestSuite()
    test = load_tests(tests)
    runner = unittest.TextTestRunner()

    # get the exit code and return it when failed
    ret = not runner.run(tests).wasSuccessful()
    sys.exit(ret)
