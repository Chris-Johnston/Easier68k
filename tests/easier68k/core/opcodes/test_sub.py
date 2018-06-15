"""
Test method for Sub opcode

"""

from easier68k.simulator.m68k import M68K
from easier68k.core.opcodes.sub import Sub
from easier68k.core.opcodes.add import Add
from easier68k.core.models.assembly_parameter import AssemblyParameter
from easier68k.core.enum.ea_mode import EAMode
from easier68k.core.enum.register import Register
from easier68k.core.enum.op_size import OpSize
from easier68k.core.enum.condition_status_code import ConditionStatusCode
from easier68k.core.util.parsing import parse_assembly_parameter
from easier68k.core.models.memory_value import MemoryValue


def test_sub():
    """
    Test to see that sub works as intended
    :return:
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    params = [AssemblyParameter(EAMode.IMM, 0b101), AssemblyParameter(EAMode.DRD, 2)]

    # Create an OPCODE to add to the data register
    add = Add(params, OpSize.BYTE)

    # Execute it twice
    add.execute(sim)
    add.execute(sim)

    # Create the OPCODE for SUB
    sub = Sub(params, OpSize.BYTE)

    sub.execute(sim)

    assert sim.get_register(Register.D2).get_value_unsigned() == 0b101

    assert sim.get_program_counter_value() == (0x1000 + (4 * 3))    # 3 OPCODEs executed

    # check the CCR

    # changed by execution
    assert sim.get_condition_status_code(ConditionStatusCode.C) is False
    assert sim.get_condition_status_code(ConditionStatusCode.V) is False
    assert sim.get_condition_status_code(ConditionStatusCode.Z) is False
    assert sim.get_condition_status_code(ConditionStatusCode.N) is False
    assert sim.get_condition_status_code(ConditionStatusCode.X) is False


def test_sub_negative():
    """
    Test to see that sub works as intended
    :return:
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    negative = parse_assembly_parameter('#-1')

    params = [negative, AssemblyParameter(EAMode.DRD, 2)]

    # Create an OPCODE to add to the data register
    add = Add(params, OpSize.BYTE)

    # Execute it twice
    add.execute(sim)
    add.execute(sim)

    sub = Sub(params, OpSize.BYTE)

    sub.execute(sim)

    assert sim.get_register(Register.D2).get_value_unsigned() == 255

    assert sim.get_program_counter_value() == (0x1000 + (4 * 3))    # 3 OPCODEs executed

    # check the CCR

    # changed by execution
    assert sim.get_condition_status_code(ConditionStatusCode.C) is False
    assert sim.get_condition_status_code(ConditionStatusCode.V) is False
    assert sim.get_condition_status_code(ConditionStatusCode.Z) is False
    assert sim.get_condition_status_code(ConditionStatusCode.N) is True
    assert sim.get_condition_status_code(ConditionStatusCode.X) is False


def test_sub_zero():
    """
    Test to see that sub works as intended
    :return:
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    negative = parse_assembly_parameter('#0')

    params = [negative, AssemblyParameter(EAMode.DRD, 2)]

    sub = Sub(params, OpSize.BYTE)

    sub.execute(sim)

    assert sim.get_register(Register.D2).get_value_unsigned() == 0

    assert sim.get_program_counter_value() == (0x1000 + 4)

    # check the CCR

    # changed by execution
    assert sim.get_condition_status_code(ConditionStatusCode.C) is False
    assert sim.get_condition_status_code(ConditionStatusCode.V) is False
    assert sim.get_condition_status_code(ConditionStatusCode.Z) is True
    assert sim.get_condition_status_code(ConditionStatusCode.N) is False
    assert sim.get_condition_status_code(ConditionStatusCode.X) is False


def test_sub_disassembles():
    """
    Test to see that sub can be assembled from some input
    """

    # cannot do
    # SUB #123, D0
    # because that gets assembled to SUBI

    # SUB.W D0, D1
    data = bytearray.fromhex('9240')

    result = Sub.disassemble_instruction(data)

    assert result is not None

    sim = M68K()

    sim.set_register(Register.D0, MemoryValue(OpSize.WORD, unsigned_int=123))
    sim.set_register(Register.D1, MemoryValue(OpSize.WORD, unsigned_int=65535))

    result.execute(sim)

    assert sim.get_register(Register.D1).get_value_unsigned() == 65412      # FF84, or (FFFF - 123)

    assert sim.get_program_counter_value() == 2


def test_ccr_carry():
    """
    Tests to see that the carry bit is set correctly

    Example case of this:
        ADD.B #$1,D0
        SUB.W D0,D1
    """

    sim = M68K()

    # 0x0001
    sim.set_register(Register.D0, MemoryValue(OpSize.BYTE, unsigned_int=1))
    # 0xFFFF as a 16 bit signed int is -1
    # sim.set_register(Register.D1, MemoryValue(OpSize.WORD, signed_int=-256))

    # D0, D1
    params = [AssemblyParameter(EAMode.DRD, 0), AssemblyParameter(EAMode.DRD, 1)]

    # SUB.W D1, D0
    sub = Sub(params, OpSize.WORD)

    sub.execute(sim)

    # result in D1 should be 65535 (FFFF)
    assert sim.get_register(Register.D1).get_value_unsigned() == 65535

    # same as C
    assert sim.get_condition_status_code(ConditionStatusCode.X) == sim.get_condition_status_code(ConditionStatusCode.C)
    # not zero
    assert not sim.get_condition_status_code(ConditionStatusCode.Z)
    # is borrow
    assert sim.get_condition_status_code(ConditionStatusCode.C)
    # is negative
    assert sim.get_condition_status_code(ConditionStatusCode.N)
    # no overflow
    assert not sim.get_condition_status_code(ConditionStatusCode.V)


def test_ccr_zero():
    """
    Tests to see that the zero bit is set correctly

    Example case of this

    SUB #1,D0 - If there is 1 in D0, then zero bit is set
    """

    sim = M68K()

    # 0x0001
    # sim.set_register(Register.D0, MemoryValue(OpSize.WORD, unsigned_int=1))
    # sim.set_register(Register.D1, MemoryValue(OpSize.WORD, unsigned_int=1))
    # 0x7FFF as a 16 bit signed int is 32767
    # sim.set_register(Register.D1, MemoryValue(OpSize.WORD, unsigned_int=0x7FFF))

    # D0, D1
    params = [AssemblyParameter(EAMode.DRD, 0), AssemblyParameter(EAMode.DRD, 1)]

    # SUB.W D0, D1
    sub = Sub(params, OpSize.WORD)
    sub.execute(sim)

    assert sim.get_register(Register.D1).get_value_unsigned() == 0x0

    assert not sim.get_condition_status_code(ConditionStatusCode.X)
    # zero bit
    assert sim.get_condition_status_code(ConditionStatusCode.Z)
    assert not sim.get_condition_status_code(ConditionStatusCode.C)
    assert not sim.get_condition_status_code(ConditionStatusCode.N)
    assert not sim.get_condition_status_code(ConditionStatusCode.V)


def test_add_assemble():
    """
    Check that assembly is the same as the input
    """

    # SUB.W D0, D1
    data = bytearray.fromhex('9240')

    result = Sub.disassemble_instruction(data)

    assm = result.assemble()

    assert data == assm
