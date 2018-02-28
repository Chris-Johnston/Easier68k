# Contributing

## Branching Method

To contribute, create a new branch and add that as a new Pull Request. Add the 
appropriate labels to your PR, and ensure that the CI build passes. If time permits,
try to ensure the quality of code by checking the pylint score from the CI build log.

Try to get another contributor to look over code before merging it to the main branch.

**TL;DR**: Branch new feature -> PR -> Pass Tests -> Seek Review -> Merge

## How to Test

This project uses a combination of doctests and pytests. As a general rule, for small and 
simple tests, use a doctest, and for anything else that is more complex, use
a pytest.

Please ensure that your tests cover most cases of expected execution, but also unexpected input.

### Running Tests

Tests are run automatically by Travis CI, but to minimize clutter, please try running locally
before you push.

You must build the package first before tests can be run. To do this, either run the following to
build and test:
```bash
cd src
# may require root
python3 setup.py test
```

Or, just to build:

```bash
cd src
# may require root
python3 setup.py install
```

Doctests are run with `python3 tests/run_doctest.py`, pytests with `python3 tests/run_pytest.py`.
Both can be run with `python3 tests/run_test_suite.py`.

Travis CI will run all code against `pylint`, but will not make any changes to your
code. Each build execution log will include the score and output from `pylint`.

### Adding a doctest

If you are unfamiliar with doctests, [please see this guide.][doctest-guide]

`tests/run_doctest.py` contains a list of all the modules that contain doctests. These
are all then loaded on testing and run one after another. If the package you are
working on is new or didn't contain tests before, please add the package to the 
list, like the others in the list.

### Adding a pytest

See `src/easier68k/core/util/conversions.py` and `tests/easier68k/core/util/test_conversions.py` 
for a working example. Pytest will locate any package under the `tests` directory that
starts with the word `test`.

Verify that your test runs by running the following:
```bash
cd tests
python3 run_pytest.py
```

[doctest-guide]: https://pymotw.com/2/doctest/ 