import unittest
from easier68k.assembler.assembler import parse


class MyTestCase(unittest.TestCase):
    @staticmethod
    def test_something():
        # Test
        f = open('easier68k/assembler/basic_test_input.x68')
        parse(f.read(-1))
