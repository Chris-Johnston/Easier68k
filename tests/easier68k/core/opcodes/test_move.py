"""
Test methods for the move command
"""

from easier68k.simulator.m68k import M68K
from easier68k.core.opcodes.move import Move
from easier68k.core.enum.ea_mode import EAMode
from easier68k.core.models.assembly_parameter import AssemblyParameter
from easier68k.core.enum.register import Register
from easier68k.core.enum.op_size import OpSize

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

    assert a.get_register_value(Register.D2) == 123

    # assert that the program counter advanced by 2 words
    assert a.get_program_counter_value() == (0x1000 + 4)

def test_move_invalid_behavior():
    """
    Test invalid behavior for move
    :return:
    """

    a = M68K()