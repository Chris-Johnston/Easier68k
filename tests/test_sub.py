"""
Test method for Sub opcode

"""

from easier68k import M68K
from easier68k.opcodes import Sub
from easier68k import AssemblyParameter
from easier68k import EAMode
from easier68k import Register
from easier68k import OpSize
from easier68k import MemoryValue
from .test_opcode_helper import run_opcode_test


def test_sub():
    """
    Test to see that it can subtract a number from another number.

    Example case used:
        MOVE.W #123,D0
        SUB.W #52,D0
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    sim.set_register(Register.D0, MemoryValue(OpSize.WORD, unsigned_int=123))

    params = [AssemblyParameter(EAMode.IMM, 52), AssemblyParameter(EAMode.DRD, 0)]

    sub = Sub(params, OpSize.WORD)  # SUB.W #52,D0

    run_opcode_test(sim, sub, Register.D0, 71, [False, False, False, False, False], 4)


def test_sub_negative():
    """
    Test to see that sub can handle negative values.

    Example case used:
        MOVE.B #2,D2
        SUB.B #-1,D2
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    sim.set_register(Register.D2, MemoryValue(OpSize.BYTE, unsigned_int=2))

    params = [AssemblyParameter(EAMode.IMM, -1), AssemblyParameter(EAMode.DRD, 2)]

    sub = Sub(params, OpSize.BYTE)  # SUB.B #-1,D2

    run_opcode_test(sim, sub, Register.D2, 3, [True, False, False, False, True], 4)


def test_sub_zero():
    """
    Test to see that subtracting 0 will result in no change to a data register.

    Example case used:
        SUB.B #0,D2
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    params = [AssemblyParameter(EAMode.IMM, 0), AssemblyParameter(EAMode.DRD, 2)]

    sub = Sub(params, OpSize.BYTE)  # SUB.B #0,D2

    run_opcode_test(sim, sub, Register.D2, 0, [False, False, True, False, False], 4)


def test_sub_disassembles():
    """
    Test to see that sub can be assembled from some input

    Example case used:
        SUB.W D0, D1 - which results in: (FFFF - 123)
    """

    data = bytearray.fromhex('9240')    # SUB.W D0, D1

    result = Sub.disassemble_instruction(data)

    assert result is not None

    sim = M68K()

    sim.set_register(Register.D0, MemoryValue(OpSize.WORD, unsigned_int=123))
    sim.set_register(Register.D1, MemoryValue(OpSize.WORD, unsigned_int=65535))

    run_opcode_test(sim, result, Register.D1, 0xFF84, [False, True, False, False, False], 2)


def test_ccr_carry():
    """
    Tests to see that the carry bit is set correctly

    Example case used:
        MOVE.B #$FF,D0
        SUB.W #$100,D0
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    sim.set_register(Register.D0, MemoryValue(OpSize.BYTE, unsigned_int=255))

    params = [AssemblyParameter(EAMode.IMM, 256), AssemblyParameter(EAMode.DRD, 0)]

    sub = Sub(params, OpSize.WORD)  # SUB.W #$100,D0

    run_opcode_test(sim, sub, Register.D0, 0xFFFF, [True, True, False, False, True], 4)


def test_ccr_overflow():
    """
    Tests to see that the overflow bit is set correctly

    Example case used:
        MOVE.B #125,D0
        MOVE.L #-4,D1
        SUB.B  D0,D1
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    sim.set_register(Register.D0, MemoryValue(OpSize.BYTE, unsigned_int=125))
    sim.set_register(Register.D1, MemoryValue(OpSize.LONG, signed_int=-4))

    params = [AssemblyParameter(EAMode.DRD, 0), AssemblyParameter(EAMode.DRD, 1)]

    sub = Sub(params, OpSize.BYTE)  # SUB.B D0,D1

    run_opcode_test(sim, sub, Register.D1, 0xFFFFFF7F, [False, False, False, True, False], 2)


def test_ccr_zero():
    """
    Tests to see that the zero bit is set correctly

    Example case used:
        SUB #0,D0 - If there is 0 in D0, then zero bit is set
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    params = [AssemblyParameter(EAMode.DRD, 0), AssemblyParameter(EAMode.DRD, 1)]

    sub = Sub(params, OpSize.WORD)  # SUB.W D0,D1

    run_opcode_test(sim, sub, Register.D1, 0x0, [False, False, True, False, False], 2)


def test_sub_assemble():
    """
    Check that assembly is the same as the input

    Example case used:
        SUB.W D0,D1
    """

    # SUB.W D0, D1
    data = bytearray.fromhex('9240')

    result = Sub.disassemble_instruction(data)

    assm = result.assemble()

    assert data == assm
