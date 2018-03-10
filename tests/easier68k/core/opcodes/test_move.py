"""
Test methods for the move command
"""

from easier68k.simulator.m68k import M68K
from easier68k.core.opcodes.move import Move
from easier68k.core.enum.ea_mode import EAMode
from easier68k.core.enum.register import Register

def test_move():

    # make a simulator class
    a = M68K()

    # move 123 to D2
    src = EAMode(EAMode.IMM, 123)
    dst = EAMode(EAMode.DRD, 2)

    # make a testing move command
    mv = Move(src, dst, 'B')

    mv.execute(a)

    assert a.get_register_value(Register.D2) == 123