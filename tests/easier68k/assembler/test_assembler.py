import pytest
from easier68k.assembler.assembler import parse


def test_basic_test_input():
    # Test
    f = open('easier68k/assembler/basic_test_input.x68')
    parse(f.read(-1))
