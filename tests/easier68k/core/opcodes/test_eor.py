"""
Test method for EOR opcode

"""

from easier68k.simulator.m68k import M68K
from easier68k.core.opcodes.eor import Eor
from easier68k.core.models.assembly_parameter import AssemblyParameter
from easier68k.core.enum.ea_mode import EAMode
from easier68k.core.enum.register import Register
from easier68k.core.enum.op_size import OpSize
from easier68k.core.models.memory_value import MemoryValue
from .test_opcode_helper import run_opcode_test


def test_eor():
    """
    Test to see that it can perform a standard EOR operation.

    Example case used:
        MOVE.B #$FF,D0
        MOVE.W #$1234,D1
        EOR.B D0, D1
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    sim.set_register(Register.D0, MemoryValue(OpSize.WORD, unsigned_int=0xFF))
    sim.set_register(Register.D1, MemoryValue(OpSize.WORD, unsigned_int=0x1234))

    params = [AssemblyParameter(EAMode.DRD, 0), AssemblyParameter(EAMode.DRD, 1)]

    eor = Eor(params, OpSize.BYTE)  # EOR.B D0, D1

    run_opcode_test(sim, eor, Register.D1, 0x12CB, [False, True, False, False, False], 2)


def test_eor_negative():
    """
    Test to see that EOR can handle negative values.

    Example case used:
        MOVE.B #1,D1
        MOVE.L #-2,D2
        EOR.L D1,D2
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    sim.set_register(Register.D1, MemoryValue(OpSize.BYTE, unsigned_int=1))
    sim.set_register(Register.D2, MemoryValue(OpSize.LONG, signed_int=-2))

    params = [AssemblyParameter(EAMode.DRD, 1), AssemblyParameter(EAMode.DRD, 2)]

    eor = Eor(params, OpSize.LONG)  # ORI.L #1,D2

    run_opcode_test(sim, eor, Register.D2, 0xFFFFFFFF, [False, True, False, False, False], 2)


def test_eor_disassembles():
    """
    Test to see that EOR can be assembled from some input

    Example case used:
        MOVE.W #$123,D0
        MOVE.B #$FF,D1
        EOR.B D1,D0
    """

    data = bytearray.fromhex('B300')    # EOR.B D1,D0

    result = Eor.disassemble_instruction(data)

    assert result is not None

    sim = M68K()

    sim.set_register(Register.D0, MemoryValue(OpSize.WORD, unsigned_int=0x123))
    sim.set_register(Register.D1, MemoryValue(OpSize.BYTE, unsigned_int=0xFF))

    run_opcode_test(sim, result, Register.D0, 0x1DC, [False, True, False, False, False], 2)


def test_ccr_n():
    """
    Tests to see that the MSB bit is set correctly

    Example case used:
        MOVE.B #$FF,D0
        MOVE.B #1,D7
        EOR.B D0,D7
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    sim.set_register(Register.D0, MemoryValue(OpSize.BYTE, unsigned_int=0xFF))
    sim.set_register(Register.D7, MemoryValue(OpSize.BYTE, unsigned_int=0x1))

    params = [AssemblyParameter(EAMode.DRD, 0), AssemblyParameter(EAMode.DRD, 7)]

    eor = Eor(params, OpSize.BYTE)  # EOR.B D0,D7

    run_opcode_test(sim, eor, Register.D7, 0xFE, [False, True, False, False, False], 2)


def test_ccr_zero():
    """
    Tests to see that the zero bit is set correctly

    Example case used:
        MOVE.B #$0,D0
        MOVE.B #$0,D1
        EOR.B D0,D1
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    sim.set_register(Register.D0, MemoryValue(OpSize.BYTE, unsigned_int=0))
    sim.set_register(Register.D1, MemoryValue(OpSize.BYTE, unsigned_int=0))

    params = [AssemblyParameter(EAMode.DRD, 0), AssemblyParameter(EAMode.DRD, 1)]

    eor = Eor(params, OpSize.BYTE)  # EOR.B D0,D1

    run_opcode_test(sim, eor, Register.D1, 0x0, [False, False, True, False, False], 2)


def test_eor_assemble():
    """
    Check that assembly is the same as the input

    Example case used:
        EOR.W D3,$1234
    """

    # EOR.W D3,$1234
    data = bytearray.fromhex('B7781234')

    result = Eor.disassemble_instruction(data)

    assm = result.assemble()

    assert data == assm
