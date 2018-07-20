"""
Test method for OR opcode

"""

from easier68k.simulator.m68k import M68K
from easier68k.core.opcodes.opcode_or import Or
from easier68k.core.models.assembly_parameter import AssemblyParameter
from easier68k.core.enum.ea_mode import EAMode
from easier68k.core.enum.register import Register
from easier68k.core.enum.op_size import OpSize
from easier68k.core.models.memory_value import MemoryValue
from .test_opcode_helper import run_opcode_test


def test_or():
    """
    Test to see that or works as intended

    Example case used:
        OR.B #10,D2
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    params = [AssemblyParameter(EAMode.IMM, 10), AssemblyParameter(EAMode.DRD, 2)]

    _or = Or(params, OpSize.BYTE)

    run_opcode_test(sim, _or, Register.D2, 10, [False, False, False, False, False], 4)

    _or.execute(sim)


def test_or_negative():
    """
    Test to see that OR can handle negative values.

    Example case used:
        OR.L #-2,D2
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    params = [AssemblyParameter(EAMode.IMM, -2), AssemblyParameter(EAMode.DRD, 2)]

    _or = Or(params, OpSize.LONG)

    run_opcode_test(sim, _or, Register.D2, 0xFFFFFFFE, [False, True, False, False, False], 6)


def test_or_disassembles():
    """
    Test to see that or can be assembled from some input

    Example case used:
        OR.W D4,D5
    """

    data = bytearray.fromhex('8A44')

    result = Or.disassemble_instruction(data)

    assert result is not None

    sim = M68K()

    run_opcode_test(sim, result, Register.D5, 0, [False, False, True, False, False], 2)


def test_ccr_n():
    """
    Tests to see that the MSB bit is set correctly

    Example case used:
        MOVE.B #$FF,D0
        OR.B #1,D0
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    sim.set_register(Register.D0, MemoryValue(OpSize.BYTE, unsigned_int=0xFF))

    params = [AssemblyParameter(EAMode.IMM, 1), AssemblyParameter(EAMode.DRD, 0)]

    _or = Or(params, OpSize.BYTE)

    run_opcode_test(sim, _or, Register.D0, 0xFF, [False, True, False, False, False], 4)


def test_ccr_zero():
    """
    Tests to see that the zero bit is set correctly

    Example case used:
        OR.L D1,D0
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    sim.set_register(Register.D0, MemoryValue(OpSize.BYTE, unsigned_int=0))

    params = [AssemblyParameter(EAMode.DRD, 1), AssemblyParameter(EAMode.DRD, 0)]

    _or = Or(params, OpSize.LONG)

    run_opcode_test(sim, _or, Register.D0, 0, [False, False, True, False, False], 2)


def test_or_assemble():
    """
    Check that assembly is the same as the input

    Example case used:
        OR.L (A4)+,D0
    """

    # OR.L (A4)+,D0
    data = bytearray.fromhex('809C')

    result = Or.disassemble_instruction(data)

    assm = result.assemble()

    assert data == assm