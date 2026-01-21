"""
Test method for NEG opcode

"""

from easier68k import M68K
from easier68k.opcodes import Neg
from easier68k import AssemblyParameter
from easier68k import EAMode
from easier68k import Register
from easier68k import OpSize
from easier68k import MemoryValue
from .test_opcode_helper import run_opcode_test


def test_neg():
    """
    Test to see that it can negate a positive number.

    Example case used:
        MOVE.W #123,D0
        NEG.W D0
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    sim.set_register(Register.D0, MemoryValue(OpSize.WORD, unsigned_int=123))

    neg = Neg([AssemblyParameter(EAMode.DRD, 0)], OpSize.WORD)  # NEG.W D0

    run_opcode_test(sim, neg, Register.D0, 0xFF85, [True, True, False, False, True], 2)


def test_neg_negative():
    """
    Test to see that neg can handle negative values.

    Example case used:
        MOVE.L #-2,D2
        NEG.L D2
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    sim.set_register(Register.D2, MemoryValue(OpSize.LONG, signed_int=-2))

    neg = Neg([AssemblyParameter(EAMode.DRD, 2)], OpSize.LONG)  # NEG.L D2

    run_opcode_test(sim, neg, Register.D2, 0x2, [True, False, False, False, True], 2)


def test_neg_disassembles():
    """
    Test to see that neg can be assembled from some input

    Example case used:
        MOVE.W #$123,D0
        NEG.B D0
    """

    data = bytearray.fromhex('4400')

    result = Neg.disassemble_instruction(data)

    assert result is not None

    sim = M68K()

    sim.set_register(Register.D0, MemoryValue(OpSize.WORD, unsigned_int=0x123))

    run_opcode_test(sim, result, Register.D0, 0x1DD, [True, True, False, False, True], 2)


def test_ccr_carry():
    """
    Tests to see that the carry bit is set correctly

    Example case used:
        MOVE.L #-100,D0
        NEG.L D0
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    sim.set_register(Register.D0, MemoryValue(OpSize.LONG, signed_int=-100))

    neg = Neg([AssemblyParameter(EAMode.DRD, 0)], OpSize.LONG)

    run_opcode_test(sim, neg, Register.D0, 100, [True, False, False, False, True], 2)


def test_ccr_overflow():
    """
    Tests to see that the overflow bit is set correctly

    Example case used:
        MOVE.L #$80,D0
        NEG.B D0
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    sim.set_register(Register.D0, MemoryValue(OpSize.LONG, unsigned_int=0x80))

    neg = Neg([AssemblyParameter(EAMode.DRD, 0)], OpSize.BYTE)

    run_opcode_test(sim, neg, Register.D0, 0x80, [True, True, False, True, True], 2)


def test_ccr_zero():
    """
    Tests to see that the zero bit is set correctly

    Example case used:
        MOVE.L #0,D0
        NEG.B  D0
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    sim.set_register(Register.D0, MemoryValue(OpSize.LONG, unsigned_int=0))

    neg = Neg([AssemblyParameter(EAMode.DRD, 0)], OpSize.BYTE)

    run_opcode_test(sim, neg, Register.D0, 0x0, [False, False, True, False, False], 2)


def test_neg_assemble():
    """
    Check that assembly is the same as the input

    Example case used:
        NEG.W (A6)+
    """

    data = bytearray.fromhex('445E')

    result = Neg.disassemble_instruction(data)

    assm = result.assemble()

    assert data == assm
