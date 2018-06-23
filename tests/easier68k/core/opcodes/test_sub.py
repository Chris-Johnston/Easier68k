"""
Test method for Sub opcode

"""

from easier68k.simulator.m68k import M68K
from easier68k.core.opcodes.sub import Sub
from easier68k.core.models.assembly_parameter import AssemblyParameter
from easier68k.core.enum.ea_mode import EAMode
from easier68k.core.enum.register import Register
from easier68k.core.enum.op_size import OpSize
# from easier68k.core.enum.condition_status_code import ConditionStatusCode
from easier68k.core.models.memory_value import MemoryValue
from tests.easier68k.core.opcodes.test_opcode_helper import run_opcode_test


def test_sub():
    """
    Test to see that it can subtract a number from another number.

    Example case used:
        MOVE.W #123,D0
        SUB.W #52,D0
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    sim.set_register(Register.D0, MemoryValue(OpSize.WORD, unsigned_int=123))

    params = [AssemblyParameter(EAMode.IMM, 52), AssemblyParameter(EAMode.DRD, 0)]

    sub = Sub(params, OpSize.WORD)  # SUB.W #52,D0

    run_opcode_test(sim, sub, Register.D0, 71, 4, [0, 0, 0, 0, 0])

    # sub.execute(sim)
    #
    # assert sim.get_register(Register.D0).get_value_unsigned() == 71  # Result should be 71
    #
    # assert sim.get_program_counter_value() == (0x1000 + 4)  # 1 OPCODE with immediate (word) data used
    #
    # # changed by execution
    # assert sim.get_condition_status_code(ConditionStatusCode.C) is False
    # assert sim.get_condition_status_code(ConditionStatusCode.V) is False
    # assert sim.get_condition_status_code(ConditionStatusCode.Z) is False
    # assert sim.get_condition_status_code(ConditionStatusCode.N) is False
    # assert sim.get_condition_status_code(ConditionStatusCode.X) is False


def test_sub_negative():
    """
    Test to see that sub can handle negative values.

    Example case used:
        MOVE.B #2,D2
        SUB.B #-1,D2
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    sim.set_register(Register.D2, MemoryValue(OpSize.BYTE, unsigned_int=2))

    params = [AssemblyParameter(EAMode.IMM, -1), AssemblyParameter(EAMode.DRD, 2)]

    sub = Sub(params, OpSize.BYTE)  # SUB.B #-1,D2

    run_opcode_test(sim, sub, Register.D2, 3, 4, [1, 0, 0, 0, 1])

    # sub.execute(sim)
    #
    # assert sim.get_register(Register.D2).get_value_signed() == 3    # 2 - (-1) = 3
    #
    # assert sim.get_program_counter_value() == (0x1000 + 4)  # 1 OPCODE with immediate (word) data used
    #
    # # changed by execution
    # assert sim.get_condition_status_code(ConditionStatusCode.C) is True
    # assert sim.get_condition_status_code(ConditionStatusCode.V) is False
    # assert sim.get_condition_status_code(ConditionStatusCode.Z) is False
    # assert sim.get_condition_status_code(ConditionStatusCode.N) is False
    # assert sim.get_condition_status_code(ConditionStatusCode.X) is True


def test_sub_zero():
    """
    Test to see that subtracting 0 will result in no change to a data register.

    Example case used:
        SUB.B #0,D2
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    params = [AssemblyParameter(EAMode.IMM, 0), AssemblyParameter(EAMode.DRD, 2)]

    sub = Sub(params, OpSize.BYTE)  # SUB.B #0,D2

    run_opcode_test(sim, sub, Register.D2, 0, 4, [0, 0, 1, 0, 0])

    # sub.execute(sim)
    #
    # assert sim.get_register(Register.D2).get_value_unsigned() == 0
    #
    # assert sim.get_program_counter_value() == (0x1000 + 4)  # 1 OPCODE with immediate (word) data used
    #
    # # changed by execution
    # assert sim.get_condition_status_code(ConditionStatusCode.C) is False
    # assert sim.get_condition_status_code(ConditionStatusCode.V) is False
    # assert sim.get_condition_status_code(ConditionStatusCode.Z) is True
    # assert sim.get_condition_status_code(ConditionStatusCode.N) is False
    # assert sim.get_condition_status_code(ConditionStatusCode.X) is False


def test_sub_disassembles():
    """
    Test to see that sub can be assembled from some input

    Example case used:
        SUB.W D0, D1 - which results in: (FFFF - 123)
    """

    data = bytearray.fromhex('9240')    # SUB.W D0, D1

    result = Sub.disassemble_instruction(data)

    assert result is not None

    sim = M68K()

    sim.set_register(Register.D0, MemoryValue(OpSize.WORD, unsigned_int=123))
    sim.set_register(Register.D1, MemoryValue(OpSize.WORD, unsigned_int=65535))

    run_opcode_test(sim, result, Register.D1, 0xFF84, 2, [0, 1, 0, 0, 0])

    # result.execute(sim)
    #
    # assert sim.get_register(Register.D1).get_value_unsigned() == 65412  # FF84, or (FFFF - 123)
    #
    # assert sim.get_program_counter_value() == 2
    #
    # # changed by execution
    # assert sim.get_condition_status_code(ConditionStatusCode.C) is False
    # assert sim.get_condition_status_code(ConditionStatusCode.V) is False
    # assert sim.get_condition_status_code(ConditionStatusCode.Z) is False
    # assert sim.get_condition_status_code(ConditionStatusCode.N) is True
    # assert sim.get_condition_status_code(ConditionStatusCode.X) is False


def test_ccr_carry():
    """
    Tests to see that the carry bit is set correctly

    Example case used:
        MOVE.B #$FF,D0
        SUB.W #$100,D0
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    sim.set_register(Register.D0, MemoryValue(OpSize.BYTE, unsigned_int=255))

    params = [AssemblyParameter(EAMode.IMM, 256), AssemblyParameter(EAMode.DRD, 0)]

    sub = Sub(params, OpSize.WORD)  # SUB.W #$100,D0

    run_opcode_test(sim, sub, Register.D0, 0xFFFF, 4, [1, 1, 0, 0, 1])

    # sub.execute(sim)

    # assert sim.get_register(Register.D0).get_value_unsigned() == 65535  # result in D0 should be FFFF
    #
    # assert sim.get_program_counter_value() == (0x1000 + 4)  # 1 OPCODE used
    #
    # # changed by execution
    # assert sim.get_condition_status_code(ConditionStatusCode.X) is True
    # assert sim.get_condition_status_code(ConditionStatusCode.Z) is False
    # assert sim.get_condition_status_code(ConditionStatusCode.C) is True
    # assert sim.get_condition_status_code(ConditionStatusCode.N) is True
    # assert sim.get_condition_status_code(ConditionStatusCode.V) is False


def test_ccr_overflow():
    """
    Tests to see that the overflow bit is set correctly

    Example case used:
        MOVE.B #125,D0
        MOVE.L #-4,D1
        SUB.B  D0,D1
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    sim.set_register(Register.D0, MemoryValue(OpSize.BYTE, unsigned_int=125))
    sim.set_register(Register.D1, MemoryValue(OpSize.LONG, signed_int=-4))

    params = [AssemblyParameter(EAMode.DRD, 0), AssemblyParameter(EAMode.DRD, 1)]

    sub = Sub(params, OpSize.BYTE)  # SUB.B D0,D1

    run_opcode_test(sim, sub, Register.D1, 0xFFFFFF7F, 2, [0, 0, 0, 1, 0])

    # sub.execute(sim)
    #
    # assert sim.get_register(Register.D1).get_value_unsigned() == 0xFFFFFF7F  # result in D1 should be -129
    #
    # assert sim.get_program_counter_value() == (0x1000 + 2)  # 1 OPCODE used
    #
    # # changed by execution
    # assert sim.get_condition_status_code(ConditionStatusCode.X) is False
    # assert sim.get_condition_status_code(ConditionStatusCode.Z) is False
    # assert sim.get_condition_status_code(ConditionStatusCode.C) is False
    # assert sim.get_condition_status_code(ConditionStatusCode.N) is False
    # assert sim.get_condition_status_code(ConditionStatusCode.V) is True


def test_ccr_zero():
    """
    Tests to see that the zero bit is set correctly

    Example case used:
        SUB #0,D0 - If there is 0 in D0, then zero bit is set
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    params = [AssemblyParameter(EAMode.DRD, 0), AssemblyParameter(EAMode.DRD, 1)]

    sub = Sub(params, OpSize.WORD)  # SUB.W D0,D1

    run_opcode_test(sim, sub, Register.D1, 0x0, 2, [0, 0, 1, 0, 0])

    # sub.execute(sim)

    # assert sim.get_register(Register.D1).get_value_unsigned() == 0x0
    #
    # assert sim.get_program_counter_value() == (0x1000 + 2)      # 1 OPCODE used
    #
    # # changed by execution
    # assert sim.get_condition_status_code(ConditionStatusCode.X) is False
    # assert sim.get_condition_status_code(ConditionStatusCode.Z) is True
    # assert sim.get_condition_status_code(ConditionStatusCode.C) is False
    # assert sim.get_condition_status_code(ConditionStatusCode.N) is False
    # assert sim.get_condition_status_code(ConditionStatusCode.V) is False


def test_sub_assemble():
    """
    Check that assembly is the same as the input

    Example case used:
        SUB.W D0,D1
    """

    # SUB.W D0, D1
    data = bytearray.fromhex('9240')

    result = Sub.disassemble_instruction(data)

    assm = result.assemble()

    assert data == assm
