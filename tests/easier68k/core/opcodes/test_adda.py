from easier68k.simulator.m68k import M68K
from easier68k.core.opcodes.adda import Adda
from easier68k.core.models.assembly_parameter import AssemblyParameter
from easier68k.core.enum.ea_mode import EAMode
from easier68k.core.enum.register import Register
from easier68k.core.enum.op_size import OpSize
from easier68k.core.util.parsing import parse_assembly_parameter
from easier68k.core.models.memory_value import MemoryValue
from .test_opcode_helper import run_opcode_test


def test_adda():
    """
    Test to see that ADDA works as intended
    Example OPCODE used:
        ADDA.W #$101,A2
    """
    sim = M68K()

    sim.set_program_counter_value(0x1000)

    params = [AssemblyParameter(EAMode.IMM, 0b101), AssemblyParameter(EAMode.ARD, 2)]

    adda = Adda(params, OpSize.WORD)

    run_opcode_test(sim, adda, Register.A2, 0b101, [False, False, False, False, False], 4)


def test_adda_negative():
    """
    Test to see that ADDA works as intended
    Example OPCODE used:
        ADDA.W #-1234,A2
    """
    sim = M68K()

    sim.set_program_counter_value(0x1000)

    negative = parse_assembly_parameter('#-1234')

    params = [negative, AssemblyParameter(EAMode.ARD, 2)]

    adda = Adda(params, OpSize.WORD)

    run_opcode_test(sim, adda, Register.A2, 0xFFFFFB2E, [False, False, False, False, False], 4)


def test_adda_zero():
    """
    Test to see that ADDA works as intended
    Example OPCODE used:
        ADDA.W #$0,A5
    """
    sim = M68K()

    sim.set_program_counter_value(0x1000)

    params = [AssemblyParameter(EAMode.IMM, 0), AssemblyParameter(EAMode.ARD, 5)]

    adda = Adda(params, OpSize.WORD)

    run_opcode_test(sim, adda, Register.A5, 0, [False, False, False, False, False], 4)


def test_adda_disassembles():
    """
    Test to see that ADDA works as intended
    Example OPCODE used:
        MOVEA.W #123,A0
        ADDA.W A0, A1
    """
    # ADDA.W A0, A1
    data = bytearray.fromhex('D2C8')

    result = Adda.disassemble_instruction(data)

    assert result is not None

    sim = M68K()

    # Load value into A0
    sim.set_register(Register.A0, MemoryValue(OpSize.WORD, unsigned_int=123))

    run_opcode_test(sim, result, Register.A1, 123, [False, False, False, False, False], 2)


def test_adda_assemble():
    """
    Test to see that ADDA works as intended
    """
    # ADDA.W A0,A1
    data = bytearray.fromhex('D2C8')

    result = Adda.disassemble_instruction(data)

    assm = result.assemble()

    assert data == assm
