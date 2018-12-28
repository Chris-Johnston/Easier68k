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

    (x, _) = BRA.is_valid("BRA.L", "$1000")
    assert x

    (x, _) = BRA.is_valid("BRA.W", "$1000")
    assert x

    (x, _) = BRA.is_valid("BRA.B", "$1000")
    assert x

    (x, y) = BRA.is_valid("BRA.L", "$1001")
    assert not x
    assert len(y) == 1

    (x, y) = BRA.is_valid("BRA.L", "$1000, Garbage")
    assert not x
    assert len(y) == 1

    (x, y) = BRA.is_valid("BRA.L", "$1001, Garbage")
    assert not x
    assert len(y) == 2

def test_bra_length():
    """
    Test BRA.get_word_length()
    :return:
    """

    # Dont bother testing size codes, see get_word_length note
    assert BRA.get_word_length("BRA", "$1000, 4100") == 1
    assert BRA.get_word_length("BRA", "$1010, 4096") == 1
    assert BRA.get_word_length("BRA", "$1000, 8194") == 2
    assert BRA.get_word_length("BRA", "$2000, 4096") == 2
    assert BRA.get_word_length("BRA", "$999, 658556") == 3
    assert BRA.get_word_length("BRA", "$5FFFFF, 4096") == 3

# All Others
# (test execute: pass and branch)