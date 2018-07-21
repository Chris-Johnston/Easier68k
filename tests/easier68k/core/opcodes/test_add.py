"""
Test method for Add opcode

"""

from easier68k.simulator.m68k import M68K
from easier68k.core.opcodes.add import Add
from easier68k.core.models.assembly_parameter import AssemblyParameter
from easier68k.core.enum.ea_mode import EAMode
from easier68k.core.enum.register import Register
from easier68k.core.enum.op_size import OpSize
from easier68k.core.util.parsing import parse_assembly_parameter
from easier68k.core.models.memory_value import MemoryValue
from .test_opcode_helper import run_opcode_test


def test_add():
    """
    Test to see that ADD works as intended
    Example OPCODE used:
        ADD.B #101,D2
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    params = [AssemblyParameter(EAMode.IMM, 101), AssemblyParameter(EAMode.DRD, 2)]

    add = Add(params, OpSize.BYTE)

    run_opcode_test(sim, add, Register.D2, 101, [False, False, False, False, False], 4)


def test_add_negative():
    """
    Test to see that ADD works as intended
    Example OPCODE used:
        ADD.B #-1,D2
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    negative = parse_assembly_parameter('#-1')

    params = [negative, AssemblyParameter(EAMode.DRD, 2)]

    add = Add(params, OpSize.BYTE)

    run_opcode_test(sim, add, Register.D2, 0xFF, [False, True, False, False, False], 4)


def test_add_zero():
    """
    Test to see that ADD works as intended
    Example OPCODE used:
        ADD.B #0,D2
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    negative = parse_assembly_parameter('#0')

    params = [negative, AssemblyParameter(EAMode.DRD, 2)]

    add = Add(params, OpSize.BYTE)

    run_opcode_test(sim, add, Register.D2, 0, [False, False, True, False, False], 4)


def test_add_disassembles():
    """
    Test to see that add can be assembled from some input
    Example OPCODE used:
        MOVE.W #123,D0
        ADD.W D0,D1
    """

    # cannot do
    # ADD #123, D0
    # because that gets assembled to ADDI

    # ADD.W D0, D1
    data = bytearray.fromhex('D240')

    result = Add.disassemble_instruction(data)

    assert result is not None

    sim = M68K()

    sim.set_register(Register.D0, MemoryValue(OpSize.WORD, unsigned_int=123))

    run_opcode_test(sim, result, Register.D1, 123, [False, False, False, False, False], 2)


def test_ccr_carry():
    """
    Tests to see that the carry bit is set correctly

    Example case of this

    MOVE #1, D0
    MOVE #$FFFF, D1
    ADD D0, D1 ; C bit will be set
    """

    sim = M68K()

    # 0x0001
    sim.set_register(Register.D0, MemoryValue(OpSize.WORD, unsigned_int=1))
    # 0xFFFF as a 16 bit signed int is -1
    sim.set_register(Register.D1, MemoryValue(OpSize.WORD, signed_int=-1))

    # D0, D1
    params = [AssemblyParameter(EAMode.DRD, 0), AssemblyParameter(EAMode.DRD, 1)]

    # Add D0, D1
    add = Add(params, OpSize.WORD)

    run_opcode_test(sim, add, Register.D1, 0, [True, False, True, False, True], 2)


def test_ccr_overflow():
    """
    Tests to see that the overflow bit is set correctly

    Example case of this

    MOVE #1, D0
    MOVE #$7FFF, D1
    ADD D0, D1 ; V bit will be set
    """

    sim = M68K()

    # 0x0001
    sim.set_register(Register.D0, MemoryValue(OpSize.WORD, unsigned_int=1))
    # 0x7FFF as a 16 bit signed int is 32767
    sim.set_register(Register.D1, MemoryValue(OpSize.WORD, unsigned_int=0x7FFF))

    # D0, D1
    params = [AssemblyParameter(EAMode.DRD, 0), AssemblyParameter(EAMode.DRD, 1)]

    # Add D0, D1
    add = Add(params, OpSize.WORD)

    run_opcode_test(sim, add, Register.D1, 0x8000, [False, True, False, True, False], 2)


def test_add_assemble():
    """
    Check that assembly is the same as the input
    Example OPCODE used:
        ADD D0, D1
    """

    # ADD D0, D1
    data = bytearray.fromhex('D240')

    result = Add.disassemble_instruction(data)

    assm = result.assemble()

    assert data == assm
