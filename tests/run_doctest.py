"""
Testing
"""

import doctest, unittest, sys

# import all of the modules that need testing
import unittest

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# build a list of all modules that contain doctests
test_modules = [
    'easier68k.conversions',
    'easier68k.parsing',
    'easier68k.split_bits',
    'easier68k.assembler',
    'easier68k.opcodes.move',
    'easier68k.opcodes.movea',
    'easier68k.opcodes.opcode_or',
    'easier68k.opcodes.eor',
    'easier68k.opcodes.ori',
    'easier68k.opcodes.add',
    'easier68k.opcodes.sub',
    'easier68k.opcodes.subq',
    'easier68k.opcodes.adda',
    'easier68k.opcodes.dc',
    'easier68k.opcodes.jsr',
    'easier68k.opcodes.rts',
    'easier68k.opcodes.lea',
    'easier68k.opcodes.neg',
    'easier68k.opcodes.simhalt',
    'easier68k.opcodes.trap',
    'easier68k.opcodes.bcc',
    'easier68k.list_file',
    'easier68k.parsing',
    'easier68k.ea_mode_bin',
    'easier68k.list_file',
    'easier68k.opcode_util',
    'easier68k.op_size',
    'easier68k.opcodes.cmp',
    'easier68k.opcodes.cmpi'
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

def run_tests():
    """
        Evaluate all of the tests that were loaded.
        """
    print('running doctests...')
    tests = unittest.TestSuite()
    test = load_tests(tests)
    runner = unittest.TextTestRunner()

    # get the exit code and return it when failed
    ret = not runner.run(tests).wasSuccessful()
    return ret


if __name__ == '__main__':
    status = run_tests()
    sys.exit(status)
