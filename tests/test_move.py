"""
Test methods for the move command
"""

from easier68k import M68K
from easier68k.opcodes import Move
from easier68k import EAMode
from easier68k import AssemblyParameter
from easier68k import Register
from easier68k import OpSize

def test_move():
    """
    Test to see that move works as intended
    :return:
    """

    # make a simulator class
    a = M68K()

    a.set_program_counter_value(0x1000)

    # test immediate -> data register

    # move 123 to D2
    src = AssemblyParameter(EAMode.IMM, 123)
    dst = AssemblyParameter(EAMode.DRD, 2)

    # make a testing move command
    mv = Move([src, dst], OpSize.BYTE)

    mv.execute(a)

    assert a.get_register(Register.D2).get_value_unsigned() == 123

    # assert that the program counter advanced by 2 words
    assert a.get_program_counter_value() == (0x1000 + 4)

def test_move_invalid_behavior():
    """
    Test invalid behavior for move
    :return:
    """

    a = M68K()