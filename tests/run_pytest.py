import sys
import pytest

def run_tests():
    print('running pytests...')
    status = pytest.main(['-x', 'tests'])
    sys.exit(status)


if __name__ == '__main__':
    run_tests()