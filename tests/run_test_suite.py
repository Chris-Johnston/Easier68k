"""
Run all the tests in one place so that it can be run by setup.py
"""
import run_doctest
import run_pytest
import unittest

class TestSuite(unittest.TestCase):
    def __init__(self):
        pass

    def run(self):
        print('aaa')
        assert not run_doctest.run_tests()
        assert not run_pytest.run_tests()

