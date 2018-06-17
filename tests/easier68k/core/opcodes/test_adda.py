from easier68k.simulator.m68k import M68K
from easier68k.core.opcodes.adda import Adda
from easier68k.core.models.assembly_parameter import AssemblyParameter
from easier68k.core.enum.ea_mode import EAMode
from easier68k.core.enum.register import Register
from easier68k.core.enum.op_size import OpSize
from easier68k.core.enum.condition_status_code import ConditionStatusCode
from easier68k.core.util.parsing import parse_assembly_parameter
from easier68k.core.models.memory_value import MemoryValue


def test_adda():
    """
    Test to see that ADDA works as intended
    Example OPCODE used: ADDA.W #$101,A2
    """
    sim = M68K()

    sim.set_program_counter_value(0x1000)

    params = [AssemblyParameter(EAMode.IMM, 0b101), AssemblyParameter(EAMode.ARD, 2)]

    adda = Adda(params, OpSize.WORD)

    adda.execute(sim)

    # Does it contain the correct value?
    assert sim.get_register(Register.A2).get_value_unsigned() == 0b101

    # Did the program counter correctly increment?
    assert sim.get_program_counter_value() == (0x1000 + 4)

    # check the CCR (ensure they're unchanged)
    assert sim.get_condition_status_code(ConditionStatusCode.C) is False
    assert sim.get_condition_status_code(ConditionStatusCode.V) is False
    assert sim.get_condition_status_code(ConditionStatusCode.Z) is False
    assert sim.get_condition_status_code(ConditionStatusCode.N) is False
    assert sim.get_condition_status_code(ConditionStatusCode.X) is False

def test_adda_negative():
    """
    Test to see that ADDA works as intended
    Example OPCODE used: ADDA.W #-1234,A2
    """
    sim = M68K()

    sim.set_program_counter_value(0x1000)

    negative = parse_assembly_parameter('#-1234')

    params = [negative, AssemblyParameter(EAMode.ARD, 2)]

    adda = Adda(params, OpSize.WORD)

    adda.execute(sim)

    # Does it contain the correct value?
    assert sim.get_register(Register.A2).get_value_unsigned() == 0xFFFFFB2E

    # Did the program counter correctly increment?
    assert sim.get_program_counter_value() == (0x1000 + 4)

    # check the CCR (ensure they're unchanged)
    assert sim.get_condition_status_code(ConditionStatusCode.C) is False
    assert sim.get_condition_status_code(ConditionStatusCode.V) is False
    assert sim.get_condition_status_code(ConditionStatusCode.Z) is False
    assert sim.get_condition_status_code(ConditionStatusCode.N) is False
    assert sim.get_condition_status_code(ConditionStatusCode.X) is False

def test_adda_zero():
    """
    Test to see that ADDA works as intended
    Example OPCODE used: ADDA.W #$0,A5
    """
    sim = M68K()

    sim.set_program_counter_value(0x1000)

    params = [AssemblyParameter(EAMode.IMM, 0b0), AssemblyParameter(EAMode.ARD, 5)]

    adda = Adda(params, OpSize.WORD)

    adda.execute(sim)

    # Does it contain the correct value?
    assert sim.get_register(Register.A5).get_value_unsigned() == 0b0

    # Did the program counter correctly increment?
    assert sim.get_program_counter_value() == (0x1000 + 4)

    # check the CCR (ensure they're unchanged)
    assert sim.get_condition_status_code(ConditionStatusCode.C) is False
    assert sim.get_condition_status_code(ConditionStatusCode.V) is False
    assert sim.get_condition_status_code(ConditionStatusCode.Z) is False
    assert sim.get_condition_status_code(ConditionStatusCode.N) is False
    assert sim.get_condition_status_code(ConditionStatusCode.X) is False

def test_adda_disassembles():
    """
    Test to see that ADDA works as intended
    """
    # ADDA.W A0, A1
    data = bytearray.fromhex('D2C8')

    result = Adda.disassemble_instruction(data)

    assert result is not None

    sim = M68K()

    # Load value into A0
    sim.set_register(Register.A0, MemoryValue(OpSize.WORD, unsigned_int=123))

    result.execute(sim)

    assert sim.get_register(Register.A1).get_value_unsigned() == 123

    assert sim.get_program_counter_value() == 2


def test_adda_assemble():
    """
    Test to see that ADDA works as intended
    """
    # ADDA.W A0,A1
    data = bytearray.fromhex('D2C8')

    result = Adda.disassemble_instruction(data)

    assm = result.assemble()

    assert data == assm
