"""
Test method for Sub opcode

"""

from easier68k.simulator.m68k import M68K
from easier68k.core.opcodes.cmpi import Cmpi
from easier68k.core.models.assembly_parameter import AssemblyParameter
from easier68k.core.enum.ea_mode import EAMode
from easier68k.core.enum.register import Register
from easier68k.core.enum.op_size import OpSize
from easier68k.core.models.memory_value import MemoryValue
from .test_opcode_helper import run_opcode_test


def test_cmpi():
    """
    Test to see that it can compare a number to another number.

    Example case used:
        MOVE.W #123,D0
        CMPI.W #52,D0
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    stored_val = 123

    sim.set_register(Register.D0, MemoryValue(OpSize.WORD, unsigned_int=stored_val))

    params = [AssemblyParameter(EAMode.IMM, 52), AssemblyParameter(EAMode.DRD, 0)]

    cmpi = Cmpi(params, OpSize.WORD)  # CMPI.W #52,D0

    run_opcode_test(sim, cmpi, Register.D0, stored_val, 4, [False, False, False, False, False])


def test_cmpi_negative():
    """
    Test to see that cmpi can handle negative values.

    Example case used:
        MOVE.B #2,D2
        CMPI.B #-1,D2
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    stored_val = 2

    sim.set_register(Register.D2, MemoryValue(OpSize.BYTE, unsigned_int=stored_val))

    params = [AssemblyParameter(EAMode.IMM, -1), AssemblyParameter(EAMode.DRD, 2)]

    cmpi = Cmpi(params, OpSize.BYTE)  # CMPI.B #-1,D2

    run_opcode_test(sim, cmpi, Register.D2, stored_val, 4, [False, False, False, False, True])


def test_cmpi_zero():
    """
    Test to see that cmpi works with 0.

    Example case used:
        MOVE.L #0,D2
        CMPI.B #0,D2
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    params = [AssemblyParameter(EAMode.IMM, 0), AssemblyParameter(EAMode.DRD, 2)]

    cmpi = Cmpi(params, OpSize.BYTE)  # CMPI.B #0,D2

    run_opcode_test(sim, cmpi, Register.D2, 0, 4, [False, False, True, False, False])


def test_cmpi_disassembles():
    """
    Test to see that cmpi can be assembled from some input

    Example case used:
        MOVE.W #$FFFF,D1
        CMPI.W #123, D1
    """

    data = bytearray.fromhex('0C41007B')    # CMPI.W #123, D1

    result = Cmpi.disassemble_instruction(data)

    assert result is not None

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    stored_value = 0xFFFF

    sim.set_register(Register.D1, MemoryValue(OpSize.WORD, unsigned_int=stored_value))

    run_opcode_test(sim, result, Register.D1, stored_value, 4, [False, True, False, False, False])


def test_ccr_carry():
    """
    Tests to see that the carry bit is set correctly

    Example case used:
        MOVE.B #$FF,D0
        CMPI.W #$100,D0
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    stored_val = 0xFF

    sim.set_register(Register.D0, MemoryValue(OpSize.BYTE, unsigned_int=stored_val))

    params = [AssemblyParameter(EAMode.IMM, 256), AssemblyParameter(EAMode.DRD, 0)]

    cmpi = Cmpi(params, OpSize.WORD)  # CMPI.W #$100,D0

    run_opcode_test(sim, cmpi, Register.D0, stored_val, 4, [False, True, False, False, True])


def test_ccr_overflow():
    """
    Tests to see that the overflow bit is set correctly

    Example case used:
        MOVE.L #-4,D1
        CMPI.B #125,D1
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    stored_val = MemoryValue(OpSize.LONG, signed_int=-4)

    sim.set_register(Register.D1, stored_val)

    params = [AssemblyParameter(EAMode.IMM, 125), AssemblyParameter(EAMode.DRD, 1)]

    cmpi = Cmpi(params, OpSize.BYTE)  # CMPI.B #125,D1

    run_opcode_test(sim, cmpi, Register.D1, stored_val.get_value_unsigned(), 4, [False, False, False, True, False])


def test_add_assemble():
    """
    Check that assembly is the same as the input

    Example case used:
        CMPI.W #$123,D3
    """

    # CMPI.W #$123,D3
    data = bytearray.fromhex('0C430123')

    result = Cmpi.disassemble_instruction(data)

    assm = result.assemble()

    assert data == assm