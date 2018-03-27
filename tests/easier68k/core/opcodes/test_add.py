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
    assert sim.get_condition_status_code(ConditionStatusCode.C) is False
    assert sim.get_condition_status_code(ConditionStatusCode.V) is False
    assert sim.get_condition_status_code(ConditionStatusCode.Z) is False
    assert sim.get_condition_status_code(ConditionStatusCode.N) is False
    assert sim.get_condition_status_code(ConditionStatusCode.X) is False


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
    assert sim.get_condition_status_code(ConditionStatusCode.C) is False
    assert sim.get_condition_status_code(ConditionStatusCode.V) is False
    assert sim.get_condition_status_code(ConditionStatusCode.Z) is False
    assert sim.get_condition_status_code(ConditionStatusCode.N) is True
    assert sim.get_condition_status_code(ConditionStatusCode.X) is False


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
    assert sim.get_condition_status_code(ConditionStatusCode.C) is False
    assert sim.get_condition_status_code(ConditionStatusCode.V) is False
    assert sim.get_condition_status_code(ConditionStatusCode.Z) is True
    assert sim.get_condition_status_code(ConditionStatusCode.N) is False
    assert sim.get_condition_status_code(ConditionStatusCode.X) is False


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


def test_ccr_carry():
    """
    Tests to see that the carry bit is set correctly

    Example case of this

    MOVE #1, D0
    MOVE #FFFF, D1
    ADD D0, D1 ; C bit will be set
    :return:
    """

    sim = M68K()

    # 0x0001
    sim.set_register_value(Register.D0, 1)
    # 0xFFFF as a 16 bit signed int is -1
    sim.set_register_value(Register.D1, 0xFFFF)

    # D0, D1
    params = [AssemblyParameter(EAMode.DRD, 0), AssemblyParameter(EAMode.DRD, 1)]

    # Add D0, D1
    add = Add(params, OpSize.WORD)

    add.execute(sim)

    # result in D1 should be 0
    assert sim.get_register_value(Register.D1) == 0

    # carries over and value is zero
    assert sim.get_condition_status_code(ConditionStatusCode.X)
    assert sim.get_condition_status_code(ConditionStatusCode.Z)
    assert sim.get_condition_status_code(ConditionStatusCode.C)

    # not negative
    assert not sim.get_condition_status_code(ConditionStatusCode.N)
    # no overflow
    assert not sim.get_condition_status_code(ConditionStatusCode.V)


def test_ccr_overflow():
    """
    Tests to see that the carry bit is set correctly

    Example case of this

    MOVE #1, D0
    MOVE #7FFF, D1
    ADD D0, D1 ; C bit will be set
    :return:
    """

    sim = M68K()

    # 0x0001
    sim.set_register_value(Register.D0, 1)
    # 0x7FFF as a 16 bit signed int is 32767
    sim.set_register_value(Register.D1, 0x7FFF)

    # D0, D1
    params = [AssemblyParameter(EAMode.DRD, 0), AssemblyParameter(EAMode.DRD, 1)]

    # Add D0, D1
    add = Add(params, OpSize.WORD)

    add.execute(sim)

    # result in D1 should be 0
    assert sim.get_register_value(Register.D1) == 0x8000

    # does not carry over and not zero
    assert not sim.get_condition_status_code(ConditionStatusCode.X)
    assert not sim.get_condition_status_code(ConditionStatusCode.Z)
    assert not sim.get_condition_status_code(ConditionStatusCode.C)

    # negative
    assert sim.get_condition_status_code(ConditionStatusCode.N)
    # overflow
    assert sim.get_condition_status_code(ConditionStatusCode.V)


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
