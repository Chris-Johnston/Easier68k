"""
Test method for Sub opcode

"""

from easier68k import M68K
from easier68k.opcodes import Subq
from easier68k import AssemblyParameter
from easier68k import EAMode
from easier68k import Register
from easier68k import OpSize
from easier68k import MemoryValue
from .test_opcode_helper import run_opcode_test


def test_subq():
    """
    Test to see that it can subtract a number from another number.

    Example case used:
        MOVE.W #123,D0
        SUBQ.W #8,D0
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    sim.set_register(Register.D0, MemoryValue(OpSize.WORD, unsigned_int=123))

    params = [AssemblyParameter(EAMode.IMM, 8), AssemblyParameter(EAMode.DRD, 0)]

    subq = Subq(params, OpSize.WORD)  # SUBQ.W #8,D0

    run_opcode_test(sim, subq, Register.D0, 0x73, [False, False, False, False, False], 2)


def test_subq_negative():
    """
    Test to see that sub can handle negative values.

    Example case used:
        MOVE.L #-2,D2
        SUBQ.L #1,D2
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    sim.set_register(Register.D2, MemoryValue(OpSize.LONG, signed_int=-2))

    params = [AssemblyParameter(EAMode.IMM, 1), AssemblyParameter(EAMode.DRD, 2)]

    subq = Subq(params, OpSize.LONG)  # SUBQ.L #1,D2

    run_opcode_test(sim, subq, Register.D2, 0xFFFFFFFD, [False, True, False, False, False], 2)


def test_subq_disassembles():
    """
    Test to see that sub can be assembled from some input

    Example case used:
        MOVE.W #$123,D0
        SUBQ.B #1,D0 - which results in 122
    """

    data = bytearray.fromhex('5300')    # SUBQ.B #1,D0

    result = Subq.disassemble_instruction(data)

    assert result is not None

    sim = M68K()

    sim.set_register(Register.D0, MemoryValue(OpSize.WORD, unsigned_int=0x123))

    run_opcode_test(sim, result, Register.D0, 0x122, [False, False, False, False, False], 2)


def test_ccr_carry():
    """
    Tests to see that the carry bit is set correctly

    Example case used:
        MOVE.W #$100,D0
        SUBQ.B #1,D0
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    sim.set_register(Register.D0, MemoryValue(OpSize.WORD, unsigned_int=0x100))

    params = [AssemblyParameter(EAMode.IMM, 1), AssemblyParameter(EAMode.DRD, 0)]

    subq = Subq(params, OpSize.BYTE)  # SUBQ.B #1,D0

    run_opcode_test(sim, subq, Register.D0, 0x1FF, [True, True, False, False, True], 2)


def test_ccr_overflow():
    """
    Tests to see that the overflow bit is set correctly

    Example case used:
        MOVE.L #-125,D0
        SUBQ.B #4,D0
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    sim.set_register(Register.D0, MemoryValue(OpSize.LONG, signed_int=-125))

    params = [AssemblyParameter(EAMode.IMM, 4), AssemblyParameter(EAMode.DRD, 0)]

    subq = Subq(params, OpSize.BYTE)  # SUBQ.B #4,D0

    run_opcode_test(sim, subq, Register.D0, 0xFFFFFF7F, [False, False, False, True, False], 2)


def test_ccr_zero():
    """
    Tests to see that the zero bit is set correctly

    Example case used:
        MOVE.L #1,D0
        SUBQ.B #1,D0
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    sim.set_register(Register.D0, MemoryValue(OpSize.LONG, unsigned_int=1))

    params = [AssemblyParameter(EAMode.IMM, 1), AssemblyParameter(EAMode.DRD, 0)]

    subq = Subq(params, OpSize.BYTE)  # SUBQ.B #1,D0

    run_opcode_test(sim, subq, Register.D0, 0x0, [False, False, True, False, False], 2)


def test_subq_assemble():
    """
    Check that assembly is the same as the input

    Example case used:
        SUBQ.W #2,D1
    """

    # SUBQ.W #2,D1
    data = bytearray.fromhex('5541')

    result = Subq.disassemble_instruction(data)

    assm = result.assemble()

    assert data == assm
