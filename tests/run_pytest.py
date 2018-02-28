import sys, os
import pytest

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_tests():
    print('running pytests...')
    status = pytest.main()
    return status


if __name__ == '__main__':
    status = run_tests()
    sys.exit(status)