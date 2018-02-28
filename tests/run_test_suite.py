"""
Run all the tests in one place so that it can be run by setup.py
"""
import run_doctest
import run_pytest
import unittest

class TestSuite(unittest.TestCase):
    def run_doctest(self):
        self.assertTrue(run_doctest.run_tests())

    def run_pytest(self):
        self.assertTrue(run_pytest.run_tests())

def run():
    unittest.main()

if __name__ == '__main__':
    run()