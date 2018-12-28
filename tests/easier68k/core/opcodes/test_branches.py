"""
Test methods for all branch opcodes
"""

from easier68k.core.opcodes.Bcc import *
from easier68k.core.enum.op_size import OpSize

def test_bcc_construction():
    b = BRA.from_str("BRA", "$2002, " + str(0x2000) )
    assert b.size == OpSize.WORD # should catch 0 offset
    assert b.offset == 0 # branching to next instruction
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
    Test if BRA assembles correctly for negative and positive offsets
    This code is definitely common for all opcodes so we only really need to test it once
    :return:
    """

    start = 0x1000 # interestingly enough, the first test would compile to 6000 0004 on Easy68k
    assert BRA.from_str("BRA", "$1006, " + str(start) ).assemble() == bytearray.fromhex("6004")
    assert BRA.from_str("BRA", "$0FF8, " + str(start) ).assemble() == bytearray.fromhex("60F6")
    assert BRA.from_str("BRA", "$1000, " + str(0x1002)).assemble() == bytearray.fromhex("60FC")

def test_bra_disassemble():
    """
    Test if BRA disassembles correctly
    Will test Offset, address, and size
    :return:
    """

    # will have a negative displacement
    b = BRA.disassemble_instruction(bytearray.fromhex("60FC"))
    assert b.offset == -4
    assert b.size == OpSize.BYTE
    #assert b.address == who knows

def test_bra_validation():
    """
    Test if BRA is_valid commands work as expected
    :return:
    """

    # BRA.is_valid("BRA", "$1000")
    #    .L, .W, .B, (odd), (even)

    (x, _) = BRA.is_valid("BRA.L", "$1000")
    assert x

    pass

def test_bra_length():
    """
    Test BRA.get_word_length()
    :return:
    """

    # BRA.getWordLength() (.b .w .l)
    pass

# All Others
# (test execute: pass and branch)