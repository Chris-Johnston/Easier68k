"""
Test method for RTS opcode

"""

from easier68k import M68K
from easier68k.opcodes import Jsr, Rts
from easier68k import Rts
from easier68k import AssemblyParameter
from easier68k import EAMode
from easier68k import Register
from easier68k import OpSize
from easier68k import MemoryValue
from .test_opcode_helper import run_opcode_test


def test_rts():
    """
    Test to see that it can start and return from a subroutine properly

    Example case used:
        JSR $1004
        RTS
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    sim.set_register(Register.A7, MemoryValue(OpSize.LONG, unsigned_int=0x1000000))

    jsr = Jsr([AssemblyParameter(EAMode.AWA, 0x1004)])

    run_opcode_test(sim, jsr, Register.A7, 0xFFFFFC, [False, False, False, False, False])

    assert sim.get_program_counter_value() == 0x1004

    assert AssemblyParameter(EAMode.ARI, 7).get_value(sim, OpSize.LONG) == 0x1004

    rts = Rts()

    run_opcode_test(sim, rts, Register.A7, 0x1000000, [False, False, False, False, False])

    assert sim.get_program_counter_value() == 0x1004


def test_rts_assemble():
    """
    Check that assembly is the same as the input

    Example case used:
        RTS
    """

    data = bytearray.fromhex('4E75')

    result = Rts.disassemble_instruction(data)

    assm = result.assemble()

    assert data == assm
