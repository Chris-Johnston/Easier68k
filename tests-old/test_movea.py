from easier68k import M68K
from easier68k.opcodes import Movea
from easier68k import AssemblyParameter
from easier68k import EAMode
from easier68k import Register
from easier68k import OpSize
from easier68k import parse_assembly_parameter
from easier68k import MemoryValue
from .test_opcode_helper import run_opcode_test


def test_movea():
    """
    Test to see that ADDA works as intended
    Example OPCODE used:
        ADDA.W #$101,A2
    """
    sim = M68K()

    sim.set_program_counter_value(0x1000)

    params = [AssemblyParameter(EAMode.IMM, 0b101), AssemblyParameter(EAMode.ARD, 2)]

    op = Movea(params, OpSize.WORD)

    run_opcode_test(sim, op, Register.A2, 0b101, [False, False, False, False, False], 4)


def test_movea_negative():
    """
    Test to see that MOVEA works as intended
    Example OPCODE used:
        MOVEA.L #-1234,A2
    """
    sim = M68K()

    sim.set_program_counter_value(0x1000)

    negative = parse_assembly_parameter('#-1234')

    params = [negative, AssemblyParameter(EAMode.ARD, 2)]

    op = Movea(params, OpSize.LONG)

    to_increment = OpSize.WORD.value + OpSize.LONG.value

    run_opcode_test(sim, op, Register.A2, 0xFFFFFB2E, [False, False, False, False, False], to_increment)


def test_movea_zero():
    """
    Test to see that MOVEA works as intended
    Example OPCODE used:
        MOVEA.W #$0,A5
    """
    sim = M68K()

    sim.set_program_counter_value(0x1000)

    params = [AssemblyParameter(EAMode.IMM, 0), AssemblyParameter(EAMode.ARD, 5)]

    op = Movea(params, OpSize.WORD)

    to_increment = OpSize.WORD.value + OpSize.WORD.value

    run_opcode_test(sim, op, Register.A5, 0, [False, False, False, False, False], to_increment)


def test_movea_disassembles():
    """
    Test to see that MOVEA works as intended
    Example OPCODE used:
        MOVEA.W #123,A0
        MOVEA.W A0, A1
    """
    # MOVEA.W A0, A1
    data = bytearray.fromhex('3248')

    result = Movea.disassemble_instruction(data)

    assert result is not None

    sim = M68K()

    # Load value into A0
    sim.set_register(Register.A0, MemoryValue(OpSize.WORD, unsigned_int=123))

    run_opcode_test(sim, result, Register.A1, 123, [False, False, False, False, False], 2)


def test_movea_assemble():
    """
    Test to see that Movea works as intended
    """
    # MOVEA.W A0,A1
    data = bytearray.fromhex('3248')

    result = Movea.disassemble_instruction(data)

    assm = result.assemble()

    assert data == assm
