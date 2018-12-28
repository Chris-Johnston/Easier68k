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

# BRA

BRA_TESTS = {
    # positive offset
    "BRA +$2": bytearray.fromhex("6002"),
    # negative offset
    "BRA -$8": bytearray.fromhex("60F8")
}

def test_bra_effect():
    """
    Test if we can BRA properly.
    :return: nothing
    """

    sim = M68K()
    sim.set_program_counter_value(0x1000)

    op = BRA([])

def test_bra_assemble():
    """
    Test if BRA assembles corrctly for negative and positive offsets
    This code is definitely common for all opcodes so we only really need to test it once
    :return:
    """

# test disassemble
# test size functions

# All Others
# (test execute)