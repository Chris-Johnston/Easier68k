import sys, os
import pytest

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import easier68k

def run_tests():
    print('running pytests...')
    print('version {}'.format(easier68k.__version__))
    status = pytest.main(['-v', '--cov=../easier68k', '--cov-config', '.coveragerc' ])
    return status


if __name__ == '__main__':
    status = run_tests()
    sys.exit(status)
