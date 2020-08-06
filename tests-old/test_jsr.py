"""
Test method for JSR opcode

"""

from easier68k import M68K
from easier68k.opcodes import Jsr
from easier68k import AssemblyParameter
from easier68k import EAMode
from easier68k import Register
from easier68k import OpSize
from easier68k import MemoryValue
from .test_opcode_helper import run_opcode_test


def test_jsr():
    """
    Test to see that it can start the subroutine properly

    Example case used:
        JSR $4000
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    sim.set_register(Register.A7, MemoryValue(OpSize.LONG, unsigned_int=0x1000000))

    jsr = Jsr([AssemblyParameter(EAMode.AWA, 0x4000)])

    run_opcode_test(sim, jsr, Register.A7, 0xFFFFFC, [False, False, False, False, False])

    assert sim.get_program_counter_value() == 0x4000

    assert AssemblyParameter(EAMode.ARI, 7).get_value(sim, OpSize.LONG) == 0x1004



def test_jsr_disassembles():
    """
    Test to see that JSR can be assembled from some input

    Example case used:
        JSR $6000
    """

    data = bytearray.fromhex('4EB86000')

    result = Jsr.disassemble_instruction(data)

    assert result is not None

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    sim.set_register(Register.A7, MemoryValue(OpSize.LONG, unsigned_int=0x1000000))

    run_opcode_test(sim, result, Register.A7, 0xFFFFFC, [False, False, False, False, False])

    assert sim.get_program_counter_value() == 0x6000

    assert AssemblyParameter(EAMode.ARI, 7).get_value(sim, OpSize.LONG) == 0x1004


def test_jsr_assemble():
    """
    Check that assembly is the same as the input

    Example case used:
        JSR (A3)
    """

    data = bytearray.fromhex('4E93')

    result = Jsr.disassemble_instruction(data)

    assm = result.assemble()

    assert data == assm