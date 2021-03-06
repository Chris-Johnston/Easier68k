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
    'easier68k.core.util.conversions',
    'easier68k.core.util.parsing',
    'easier68k.core.util.split_bits',
    'easier68k.assembler.assembler',
    'easier68k.core.opcodes.move',
    'easier68k.core.opcodes.movea',
    'easier68k.core.opcodes.opcode_or',
    'easier68k.core.opcodes.eor',
    'easier68k.core.opcodes.ori',
    'easier68k.core.opcodes.add',
    'easier68k.core.opcodes.sub',
    'easier68k.core.opcodes.subq',
    'easier68k.core.opcodes.adda',
    'easier68k.core.opcodes.dc',
    'easier68k.core.opcodes.jsr',
    'easier68k.core.opcodes.rts',
    'easier68k.core.opcodes.lea',
    'easier68k.core.opcodes.neg',
    'easier68k.core.opcodes.simhalt',
    'easier68k.core.opcodes.trap',
    'easier68k.core.opcodes.bcc',
    'easier68k.core.models.list_file',
    'easier68k.core.util.parsing',
    'easier68k.core.enum.ea_mode_bin',
    'easier68k.core.models.list_file',
    'easier68k.core.util.opcode_util',
    'easier68k.core.enum.op_size',
    'easier68k.core.opcodes.cmp',
    'easier68k.core.opcodes.cmpi'
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
