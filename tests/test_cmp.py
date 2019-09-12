"""
Tests for the CMP opcode
Ensures that all of the CCR bits are being set correctly
"""

from easier68k import M68K
from easier68k.opcodes import Cmp
from easier68k import AssemblyParameter
from easier68k import EAMode
from easier68k import Register
from easier68k import OpSize
from easier68k import MemoryValue
from .test_opcode_helper import run_opcode_test


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

    stored_val = 123    # The value stored at D1

    # check that the program counter moved ahead by 2 bytes (1 word)
    # which is how long the CMP.B D0, D1 instruction is
    correct_incrementation = 2

    # initialize the values of D0 and D1
    sim.set_register(Register.D0, MemoryValue(OpSize.LONG, unsigned_int=0x00c0ffee))
    sim.set_register(Register.D1, MemoryValue(OpSize.BYTE, unsigned_int=stored_val))

    # compare D0 to D1
    params = [AssemblyParameter(EAMode.DRD, 0), AssemblyParameter(EAMode.DRD, 1)]

    cmp = Cmp(params, OpSize.BYTE)
    run_opcode_test(sim, cmp, Register.D1, stored_val, [False, True, False, True, True], correct_incrementation)

    # now do the same tests with CMP.W, CMP.L
    cmp = Cmp(params, OpSize.WORD)
    run_opcode_test(sim, cmp, Register.D1, stored_val, [False, False, False, False, True], correct_incrementation)

    # L
    # C and N are set
    cmp = Cmp(params, OpSize.LONG)
    run_opcode_test(sim, cmp, Register.D1, stored_val, [False, True, False, False, True], correct_incrementation)
