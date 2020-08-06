"""
Test methods for the LEA command
"""

from easier68k import M68K
from easier68k.opcodes import Lea
from easier68k import EAMode
from easier68k import AssemblyParameter
from easier68k import Register

def test_lea():
    """
    Test to see that move works as intended
    :return:
    """

    # make a simulator class
    a = M68K()

    # test immediate -> data register

    # move 124 to A3
    # 123 is not an aligned address
    src = AssemblyParameter(EAMode.AbsoluteLongAddress, 124)
    dst = AssemblyParameter(EAMode.ARD, 3)

    # make a testing move command
    lea = Lea([src, dst])

    lea.execute(a)

    assert a.get_register(Register.A3).get_value_unsigned() == 124
