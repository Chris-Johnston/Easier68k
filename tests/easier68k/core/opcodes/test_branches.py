"""
Test methods for all branch opcodes
"""

from easier68k.core.opcodes.bcc import *
from easier68k.core.enum.op_size import OpSize

def test_bcc_construction():
    b = Bra.from_str("BRA", "$2002, " + str(0x2000) )
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

    op = Bra([0x2000, 0x1000])
    op.execute(sim)

    assert sim.get_program_counter_value() == 0x2000

    # TEST NEGATIVE OFFSET
    sim.set_program_counter_value(0x2006)

    op = Bra([0x2000, 0x2006])
    op.execute(sim)

    assert sim.get_program_counter_value() == 0x2000


def test_bra_assemble():
    """
    Test if BRA assembles correctly for negative and positive offsets
    This code is definitely common for all opcodes so we only really need to test it once
    :return:
    """

    start = 0x1000 # interestingly enough, the first test would compile to 6000 0004 on Easy68k
    assert Bra.from_str("BRA", "$1006, " + str(start) ).assemble() == bytearray.fromhex("6004")
    assert Bra.from_str("BRA", "$0FF8, " + str(start) ).assemble() == bytearray.fromhex("60F6")
    assert Bra.from_str("BRA", "$1000, " + str(0x1002)).assemble() == bytearray.fromhex("60FC")

def test_bra_disassemble():
    """
    Test if BRA disassembles correctly
    Will test Offset, address, and size
    :return:
    """

    # will have a negative displacement
    b = Bra.disassemble_instruction(bytearray.fromhex("60FC"))
    assert b.offset == -4
    assert b.size == OpSize.BYTE
    #assert b.address == who knows

def test_bra_validation():
    """
    Test if BRA is_valid commands work as expected
    :return:
    """

    (x, _) = Bra.is_valid("BRA.L", "$1000")
    assert x

    (x, _) = Bra.is_valid("BRA.W", "$1000")
    assert x

    (x, _) = Bra.is_valid("BRA.B", "$1000")
    assert x

    (x, y) = Bra.is_valid("BRA.L", "$1001")
    assert not x
    assert len(y) == 1

    (x, y) = Bra.is_valid("BRA.L", "$1000, Garbage")
    assert not x
    assert len(y) == 1

    (x, y) = Bra.is_valid("BRA.L", "$1001, Garbage")
    assert not x
    assert len(y) == 2

def test_bra_length():
    """
    Test BRA.get_word_length()
    :return:
    """

    # Dont bother testing size codes, see get_word_length note
    assert Bra.get_word_length("BRA", "$1000, 4100") == 1
    assert Bra.get_word_length("BRA", "$1010, 4096") == 1
    assert Bra.get_word_length("BRA", "$1000, 8194") == 2
    assert Bra.get_word_length("BRA", "$2000, 4096") == 2
    assert Bra.get_word_length("BRA", "$999, 658556") == 3
    assert Bra.get_word_length("BRA", "$5FFFFF, 4096") == 3

# All Others
# (test execute: pass and branch)
# CCR = XNZVC

def test_bhi():
    sim = M68K()
    sim.set_program_counter_value(0x1000)

    sim.set_ccr_reg(None, None, False, None, False)

    op = Bhi([0x2000, 0x1000])
    op.execute(sim)

    assert sim.get_program_counter_value() == 0x2000

    sim.set_program_counter_value(0x1000)
    sim.set_ccr_reg(None, None, True, None, False)
    op.execute(sim)

    assert sim.get_program_counter_value() == 0x1000

def test_bls():
    sim = M68K()
    sim.set_program_counter_value(0x1000)

    sim.set_ccr_reg(None, None, True, None, True)

    op = Bls([0x2000, 0x1000])
    op.execute(sim)

    assert sim.get_program_counter_value() == 0x2000

    sim.set_program_counter_value(0x1000)
    sim.set_ccr_reg(None, None, False, None, False)
    op.execute(sim)

    assert sim.get_program_counter_value() == 0x1000

def test_bcc():
    sim = M68K()
    sim.set_program_counter_value(0x1000)

    sim.set_ccr_reg(None, None, None, None, False)

    op = Bcc([0x2000, 0x1000])
    op.execute(sim)

    assert sim.get_program_counter_value() == 0x2000

    sim.set_program_counter_value(0x1000)
    sim.set_ccr_reg(None, None, None, None, True)
    op.execute(sim)

    assert sim.get_program_counter_value() == 0x1000

def test_bcs():
    sim = M68K()
    sim.set_program_counter_value(0x1000)

    sim.set_ccr_reg(None, None, None, None, True)

    op = Bcs([0x2000, 0x1000])
    op.execute(sim)

    assert sim.get_program_counter_value() == 0x2000

    sim.set_program_counter_value(0x1000)
    sim.set_ccr_reg(None, None, None, None, False)
    op.execute(sim)

    assert sim.get_program_counter_value() == 0x1000

def test_bne():
    sim = M68K()
    sim.set_program_counter_value(0x1000)

    sim.set_ccr_reg(None, None, False, None, None)

    op = Bne([0x2000, 0x1000])
    op.execute(sim)

    assert sim.get_program_counter_value() == 0x2000

    sim.set_program_counter_value(0x1000)
    sim.set_ccr_reg(None, None, True, None, None)
    op.execute(sim)

    assert sim.get_program_counter_value() == 0x1000

def test_beq():
    sim = M68K()
    sim.set_program_counter_value(0x1000)

    sim.set_ccr_reg(None, None, True, None, None)

    op = Beq([0x2000, 0x1000])
    op.execute(sim)

    assert sim.get_program_counter_value() == 0x2000

    sim.set_program_counter_value(0x1000)
    sim.set_ccr_reg(None, None, False, None, None)
    op.execute(sim)

    assert sim.get_program_counter_value() == 0x1000

def test_bvc():
    sim = M68K()
    sim.set_program_counter_value(0x1000)

    sim.set_ccr_reg(None, None, None, False, None)

    op = Bvc([0x2000, 0x1000])
    op.execute(sim)

    assert sim.get_program_counter_value() == 0x2000

    sim.set_program_counter_value(0x1000)
    sim.set_ccr_reg(None, None, None, True, None)
    op.execute(sim)

    assert sim.get_program_counter_value() == 0x1000

def test_bvs():
    sim = M68K()
    sim.set_program_counter_value(0x1000)

    sim.set_ccr_reg(None, None, None, True, None)

    op = Bvs([0x2000, 0x1000])
    op.execute(sim)

    assert sim.get_program_counter_value() == 0x2000

    sim.set_program_counter_value(0x1000)
    sim.set_ccr_reg(None, None, None, False, None)
    op.execute(sim)

    assert sim.get_program_counter_value() == 0x1000

def test_bpl():
    sim = M68K()
    sim.set_program_counter_value(0x1000)

    sim.set_ccr_reg(None, False, None, None, None)
    op = Bpl([0x2000, 0x1000])
    op.execute(sim)

    assert sim.get_program_counter_value() == 0x2000

    sim.set_program_counter_value(0x1000)
    sim.set_ccr_reg(None, True, None, None, None)
    op.execute(sim)

    assert sim.get_program_counter_value() == 0x1000

def test_bmi():
    sim = M68K()
    sim.set_program_counter_value(0x1000)

    sim.set_ccr_reg(None, True, None, None, None)
    op = Bmi([0x2000, 0x1000])
    op.execute(sim)

    assert sim.get_program_counter_value() == 0x2000

    sim.set_program_counter_value(0x1000)
    sim.set_ccr_reg(None, False, None, None, None)
    op.execute(sim)

    assert sim.get_program_counter_value() == 0x1000

# CCR = XNZVC
def test_bge():

    sim = M68K()
    op = Bge([0x2000, 0x1000])

    sim.set_program_counter_value(0x1000)
    sim.set_ccr_reg(None, True, None, True, None)
    op.execute(sim)

    assert sim.get_program_counter_value() == 0x2000

    sim.set_program_counter_value(0x1000)
    sim.set_ccr_reg(None, False, None, False, None)
    op = Bge([0x2000, 0x1000])
    op.execute(sim)

    assert sim.get_program_counter_value() == 0x2000

    sim.set_program_counter_value(0x1000)
    sim.set_ccr_reg(None, False, None, True, None)
    op = Bge([0x2000, 0x1000])
    op.execute(sim)

    assert sim.get_program_counter_value() == 0x1000

def test_blt():

    sim = M68K()
    op = Blt([0x2000, 0x1000])

    sim.set_program_counter_value(0x1000)
    sim.set_ccr_reg(None, False, None, False, None)
    op.execute(sim)

    assert sim.get_program_counter_value() == 0x1000

    sim.set_program_counter_value(0x1000)
    sim.set_ccr_reg(None, True, None, True, None)
    op = Blt([0x2000, 0x1000])
    op.execute(sim)

    assert sim.get_program_counter_value() == 0x1000

    sim.set_program_counter_value(0x1000)
    sim.set_ccr_reg(None, False, None, True, None)
    op = Blt([0x2000, 0x1000])
    op.execute(sim)

    assert sim.get_program_counter_value() == 0x2000

# CCR = XNZVC
def test_bgt():

    sim = M68K()
    op = Bgt([0x2000, 0x1000])

    sim.set_program_counter_value(0x1000)
    sim.set_ccr_reg(None, True, False, True, None)
    op.execute(sim)

    assert sim.get_program_counter_value() == 0x2000

    sim.set_program_counter_value(0x1000)
    sim.set_ccr_reg(None, False, False, False, None)
    op = Bgt([0x2000, 0x1000])
    op.execute(sim)

    assert sim.get_program_counter_value() == 0x2000

    sim.set_program_counter_value(0x1000)
    sim.set_ccr_reg(None, False, None, True, None)
    op = Bgt([0x2000, 0x1000])
    op.execute(sim)

    assert sim.get_program_counter_value() == 0x1000

# CCR = XNZVC
def test_ble():

    sim = M68K()
    op = Ble([0x2000, 0x1000])

    sim.set_program_counter_value(0x1000)
    sim.set_ccr_reg(None, True, False, False, None)
    op.execute(sim)

    assert sim.get_program_counter_value() == 0x2000

    sim.set_program_counter_value(0x1000)
    sim.set_ccr_reg(None, True, False, True, None)
    op = Ble([0x2000, 0x1000])
    op.execute(sim)

    assert sim.get_program_counter_value() == 0x1000

    sim.set_program_counter_value(0x1000)
    sim.set_ccr_reg(None, False, False, False, None)
    op = Ble([0x2000, 0x1000])
    op.execute(sim)

    assert sim.get_program_counter_value() == 0x1000
