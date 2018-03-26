"""
Test method for Add opcode

"""

from easier68k.simulator.m68k import M68K
from easier68k.core.opcodes.add import Add
from easier68k.core.models.assembly_parameter import AssemblyParameter
from easier68k.core.enum.ea_mode import EAMode
from easier68k.core.enum.register import Register
from easier68k.core.enum.op_size import OpSize
from easier68k.core.enum.condition_status_code import ConditionStatusCode
from easier68k.core.util.parsing import parse_assembly_parameter

def test_add():
    """
    Test to see that or works as intended
    :return:
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    params = [AssemblyParameter(EAMode.IMM, 0b101), AssemblyParameter(EAMode.DRD, 2)]

    add = Add(params, OpSize.BYTE)

    add.execute(sim)

    assert sim.get_register_value(Register.D2) == 0b101

    assert sim.get_program_counter_value() == (0x1000 + 4)

    # check the CCR

    # changed by execution
    assert sim.get_condition_status_code(ConditionStatusCode.C) == 0
    assert sim.get_condition_status_code(ConditionStatusCode.V) == 0
    assert sim.get_condition_status_code(ConditionStatusCode.Z) == 0
    assert sim.get_condition_status_code(ConditionStatusCode.N) == 0
    assert sim.get_condition_status_code(ConditionStatusCode.X) == 0


def test_add_negative():
    """
    Test to see that or works as intended
    :return:
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    negative = parse_assembly_parameter('#-1')

    print(negative)

    params = [negative, AssemblyParameter(EAMode.DRD, 2)]

    add = Add(params, OpSize.BYTE)

    add.execute(sim)

    assert sim.get_register_value(Register.D2) == 255

    assert sim.get_program_counter_value() == (0x1000 + 4)

    # check the CCR

    # changed by execution
    assert sim.get_condition_status_code(ConditionStatusCode.C) == 0
    assert sim.get_condition_status_code(ConditionStatusCode.V) == 0
    assert sim.get_condition_status_code(ConditionStatusCode.Z) == 0
    assert sim.get_condition_status_code(ConditionStatusCode.N) == 1
    assert sim.get_condition_status_code(ConditionStatusCode.X) == 0


def test_add_zero():
    """
    Test to see that or works as intended
    :return:
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    negative = parse_assembly_parameter('#0')

    params = [negative, AssemblyParameter(EAMode.DRD, 2)]

    add = Add(params, OpSize.BYTE)

    add.execute(sim)

    assert sim.get_register_value(Register.D2) == 0

    assert sim.get_program_counter_value() == (0x1000 + 4)

    # check the CCR

    # changed by execution
    assert sim.get_condition_status_code(ConditionStatusCode.C) == 0
    assert sim.get_condition_status_code(ConditionStatusCode.V) == 0
    assert sim.get_condition_status_code(ConditionStatusCode.Z) == 1
    assert sim.get_condition_status_code(ConditionStatusCode.N) == 0
    assert sim.get_condition_status_code(ConditionStatusCode.X) == 0


def test_add_disassembles():
    """
    Test to see that add can be assembled from some input
    :return:
    """

    # cannot do
    # ADD #123, D0
    # because that gets assembled to ADDI

    # ADD D0, D1
    data = bytearray.fromhex('D2 40')

    result = Add.disassemble_instruction(data)

    assert result is not None

    sim = M68K()

    sim.set_register_value(Register.D0, 123)

    result.execute(sim)

    assert sim.get_register_value(Register.D1) == 123

    assert sim.get_program_counter_value() == 2


def test_add_assemble():
    """
    Check that assembly is the same as the input
    :return:
    """

    # ADD D0, D1
    data = bytearray.fromhex('D2 40')

    result = Add.disassemble_instruction(data)

    assm = result.assemble()

    assert data == assm
