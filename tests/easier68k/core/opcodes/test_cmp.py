"""
Tests for the CMP opcode
Ensures that all of the CCR bits are being set correctly
"""

from easier68k.simulator.m68k import M68K
from easier68k.core.opcodes.cmp import Cmp
from easier68k.core.models.assembly_parameter import AssemblyParameter
from easier68k.core.enum.ea_mode import EAMode
from easier68k.core.enum.register import Register
from easier68k.core.enum.op_size import OpSize
from easier68k.core.enum.condition_status_code import ConditionStatusCode
from easier68k.core.util.parsing import parse_assembly_parameter
from easier68k.core.models.memory_value import MemoryValue

def test_cmp():
    """
    Test to see that CMP sets the CCR bits

    MOVE.L #$00C0FFEE, D0
    MOVE.W #123, D1
    CMP.B D0, D1

    :return:
    """
    sim = M68K()
    sim.set_program_counter_value(0x1000)

    # initialize the values of D0 and D1
    sim.set_register(Register.D0, MemoryValue(OpSize.LONG, unsigned_int=0x00c0ffee))
    sim.set_register(Register.D1, MemoryValue(OpSize.BYTE, unsigned_int=123))

    # compare D0 to D1
    params = [AssemblyParameter(EAMode.DRD, 0), AssemblyParameter(EAMode.DRD, 1)]
    cmp = Cmp(params, OpSize.BYTE)
    cmp.execute(sim)
    # check that the program counter moved ahead by 2 bytes (1 word)
    # which is how long the CMP.B D0, D1 instruction is
    assert sim.get_program_counter_value() == (0x1000 + 2)

    # check that the CCR bits were set correctly
    assert sim.get_condition_status_code(ConditionStatusCode.C) is True
    assert sim.get_condition_status_code(ConditionStatusCode.V) is True
    assert sim.get_condition_status_code(ConditionStatusCode.Z) is False
    assert sim.get_condition_status_code(ConditionStatusCode.N) is True
    assert sim.get_condition_status_code(ConditionStatusCode.X) is False

    # now do the same tests with CMP.W, CMP.L
    cmp = Cmp(params, OpSize.WORD)
    cmp.execute(sim)

    assert sim.get_program_counter_value() == (0x1000 + 4)
    # W
    # only C is set

    assert sim.get_condition_status_code(ConditionStatusCode.C) is True
    assert sim.get_condition_status_code(ConditionStatusCode.V) is False
    assert sim.get_condition_status_code(ConditionStatusCode.Z) is False
    assert sim.get_condition_status_code(ConditionStatusCode.N) is False
    assert sim.get_condition_status_code(ConditionStatusCode.X) is False

    # L
    # C and N are set
    cmp = Cmp(params, OpSize.LONG)
    cmp.execute(sim)

    assert sim.get_program_counter_value() == (0x1000 + 6)

    assert sim.get_condition_status_code(ConditionStatusCode.C) is True
    assert sim.get_condition_status_code(ConditionStatusCode.V) is False
    assert sim.get_condition_status_code(ConditionStatusCode.Z) is False
    assert sim.get_condition_status_code(ConditionStatusCode.N) is True
    assert sim.get_condition_status_code(ConditionStatusCode.X) is False


