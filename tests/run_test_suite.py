"""
Run all the tests in one place so that it can be run by setup.py
"""
import run_doctest
import run_pytest

run_doctest.run_tests()
run_pytest.run_tests()