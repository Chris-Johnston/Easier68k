import unittest
from src.easier68k.assembler.assembler import parse


class MyTestCase(unittest.TestCase):
    @staticmethod
    def test_something():
        # Test
        f = open('basic_test_input.x68')
        parse(f.read(-1))
