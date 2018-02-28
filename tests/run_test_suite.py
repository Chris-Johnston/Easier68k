"""
Run all the tests in one place so that it can be run by setup.py
"""

import run_doctest

run_doctest.run_tests()
pytest.main()