"""
Test methods for all branch opcodes
"""

from easier68k.simulator.m68k import M68K
from easier68k.core.opcodes.Bcc import *
from easier68k.core.models.assembly_parameter import AssemblyParameter
from easier68k.core.enum.ea_mode import EAMode
from easier68k.core.enum.register import Register
from easier68k.core.enum.op_size import OpSize
from easier68k.core.models.memory_value import MemoryValue
from .test_opcode_helper import run_opcode_test

def test_bcc_construction():
    b = BRA.from_str("BRA", "$2002, " + str(0x2000) )
    assert b.size == OpSize.BYTE
    assert b.offset == 2
    assert b.address == 0x2000
    assert b.operand == 0x2002

def test_bra_effect():
    """
    Test if we can BRA properly.
    :return: nothing
    """

    sim = M68K()
    sim.set_program_counter_value(0x1000)

    op = BRA([0x2000, 0x1000])
    op.execute(sim)

    assert sim.get_program_counter_value() == 0x2000

    # TEST NEGATIVE OFFSET
    sim.set_program_counter_value(0x2006)

    op = BRA([0x2000, 0x2006])
    op.execute(sim)

    assert sim.get_program_counter_value() == 0x2000


def test_bra_assemble():
    """
    Test if BRA assembles corrctly for negative and positive offsets
    This code is definitely common for all opcodes so we only really need to test it once
    :return:
    """
    start = 0x2000
    assert BRA.from_str("BRA", "$2002, " + str(start) ).assemble() == bytearray(b'\x60\x02')
    #assert str(BRA.from_str("BRA", "$1FF8, " + str(start) )) == bytearray.fromhex("60F8")

# test disassemble
# test size functions

# All Others
# (test execute)