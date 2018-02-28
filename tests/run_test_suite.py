"""
Run all the tests in one place so that it can be run by setup.py
"""
import run_doctest
import run_pytest
import unittest

class TestSuite(unittest.TestCase):

    def test_doctest(self):
        self.assertTrue(0 == run_doctest.run_tests())

    def test_pytest(self):
        self.assertTrue(0 == run_pytest.run_tests())

def run():
    unittest.main()

if __name__ == '__main__':
    run()