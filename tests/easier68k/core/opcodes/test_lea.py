"""
Test methods for the LEA command
"""

from easier68k.simulator.m68k import M68K
from easier68k.core.opcodes.lea import Lea
from easier68k.core.enum.ea_mode import EAMode
from easier68k.core.models.assembly_parameter import AssemblyParameter
from easier68k.core.enum.register import Register

def test_lea():
    """
    Test to see that move works as intended
    :return:
    """

    # make a simulator class
    a = M68K()

    # test immediate -> data register

    # move 123 to A3
    src = AssemblyParameter(EAMode.ALA, 123)
    dst = AssemblyParameter(EAMode.ARD, 3)

    # make a testing move command
    lea = Lea(src, dst)

    lea.execute(a)

    assert a.get_register_value(Register.A3) == 123
