"""
Test method for OR opcode

"""

from easier68k.simulator.m68k import M68K
from easier68k.core.opcodes.opcode_or import Or
from easier68k.core.models.assembly_parameter import AssemblyParameter
from easier68k.core.enum.ea_mode import EAMode
from easier68k.core.enum.register import Register
from easier68k.core.enum.op_size import OpSize

def test_or():
    """
    Test to see that or works as intended
    :return:
    """

    sim = M68K()

    sim.set_program_counter_value(0x1000)

    params = [AssemblyParameter(EAMode.IMM, 0b101), AssemblyParameter(EAMode.DRD, 2)]

    _or = Or(params, OpSize.BYTE)

    _or.execute(sim)

    assert sim.get_register_value(Register.D2) == 0b101

    assert sim.get_program_counter_value() == (0x1000 + 4)