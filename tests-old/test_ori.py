"""
Test method for ORI opcode

"""

from easier68k import M68K
from easier68k.opcodes import Ori
from easier68k import AssemblyParameter
from easier68k import EAMode
from easier68k import Register
from easier68k import OpSize
from easier68k import MemoryValue
from .test_opcode_helper import run_opcode_test


def test_ori():
    """
    Test to see that it can perform a standard ORI operation.

    Example case used:
        MOVE.W #$1234,D1
        ORI.B #$FF, D1
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    sim.set_register(Register.D1, MemoryValue(OpSize.WORD, unsigned_int=0x1234))

    params = [AssemblyParameter(EAMode.IMM, 0xFF), AssemblyParameter(EAMode.DRD, 1)]

    ori = Ori(params, OpSize.BYTE)  # ORI.B #$FF, D1

    run_opcode_test(sim, ori, Register.D1, 0x12FF, [False, True, False, False, False], 4)


def test_ori_negative():
    """
    Test to see that ORI can handle negative values.

    Example case used:
        MOVE.L #-2,D2
        ORI.L #1,D2
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    sim.set_register(Register.D2, MemoryValue(OpSize.LONG, signed_int=-2))

    params = [AssemblyParameter(EAMode.IMM, 1), AssemblyParameter(EAMode.DRD, 2)]

    ori = Ori(params, OpSize.LONG)  # ORI.L #1,D2

    run_opcode_test(sim, ori, Register.D2, 0xFFFFFFFF, [False, True, False, False, False], 6)


def test_ori_disassembles():
    """
    Test to see that sub can be assembled from some input

    Example case used:
        MOVE.W #$123,D0
        ORI.B #1,D0
    """

    data = bytearray.fromhex('00000001')    # ORI.B #1,D0

    result = Ori.disassemble_instruction(data)

    assert result is not None

    sim = M68K()

    sim.set_register(Register.D0, MemoryValue(OpSize.WORD, unsigned_int=0x123))

    run_opcode_test(sim, result, Register.D0, 0x123, [False, False, False, False, False], 4)


def test_ccr_n():
    """
    Tests to see that the MSB bit is set correctly

    Example case used:
        MOVE.B #$FF,D0
        ORI.B #1,D0
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    sim.set_register(Register.D0, MemoryValue(OpSize.BYTE, unsigned_int=0xFF))

    params = [AssemblyParameter(EAMode.IMM, 1), AssemblyParameter(EAMode.DRD, 0)]

    ori = Ori(params, OpSize.BYTE)  # ORI.B #1,D0

    run_opcode_test(sim, ori, Register.D0, 0xFF, [False, True, False, False, False], 4)


def test_ccr_zero():
    """
    Tests to see that the zero bit is set correctly

    Example case used:
        MOVE.B #$0,D0
        ORI.B #0,D0
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    sim.set_register(Register.D0, MemoryValue(OpSize.BYTE, unsigned_int=0))

    params = [AssemblyParameter(EAMode.IMM, 0), AssemblyParameter(EAMode.DRD, 0)]

    ori = Ori(params, OpSize.BYTE)  # ORI.B #0,D0

    run_opcode_test(sim, ori, Register.D0, 0x0, [False, False, True, False, False], 4)


def test_ori_assemble():
    """
    Check that assembly is the same as the input

    Example case used:
        ORI.W #$FFFF,$1234
    """

    # ORI.W #$FFFF,$1234
    data = bytearray.fromhex('0078FFFF1234')

    result = Ori.disassemble_instruction(data)

    assm = result.assemble()

    assert data == assm
