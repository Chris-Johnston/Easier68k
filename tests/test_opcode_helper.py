"""
Helper method for OPCODE unit tests.

"""

from easier68k import M68K
from easier68k import Register
from easier68k.opcodes import Opcode
from easier68k import MemoryValue
from easier68k import ConditionStatusCode


def run_opcode_test(sim: M68K, opcode: Opcode, reg_check: Register, expected_val: int, expected_ccr: list,
                    program_increment: int = None):
    """
    Executes the OPCODE and checks to see if it executes correctly
    (by checking the affected register and the CCR).
    :param sim: The simulator
    :param opcode: The OPCODE to execute
    :param reg_check: The register to check
    :param expected_val: unsigned value of the expected value for the register
    :param expected_ccr: A list of bools of what the CCR should look like after execution
    :param program_increment: how much the program should increment after execution
    :return: None
    """

    assert expected_ccr.__len__() == 5  # Size should always be 5

    if program_increment is not None:
        program_val = sim.get_program_counter_value()   # Get the counter value before execution

    opcode.execute(sim)

    assert sim.get_register(reg_check).get_value_unsigned() == expected_val

    if program_increment is not None:
        assert sim.get_program_counter_value() == (program_val + program_increment)

    # changed by execution
    assert sim.get_condition_status_code(ConditionStatusCode.X) == expected_ccr[0]
    assert sim.get_condition_status_code(ConditionStatusCode.N) == expected_ccr[1]
    assert sim.get_condition_status_code(ConditionStatusCode.Z) == expected_ccr[2]
    assert sim.get_condition_status_code(ConditionStatusCode.V) == expected_ccr[3]
    assert sim.get_condition_status_code(ConditionStatusCode.C) == expected_ccr[4]
