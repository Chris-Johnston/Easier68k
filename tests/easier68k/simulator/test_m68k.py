import pytest

from easier68k.simulator.m68k import M68K
from easier68k.core.enum.register import Register

def test_program_counter():
    """
    Tests for the m68k Program Counter register
    :return:
    """

    a = M68K()

    # ensure that its value defaults to zero
    assert a.get_program_counter_value() == 0

    # try setting w/o errors
    a.set_program_counter_value(0x3200)

    # ensure that this value can be retrieved without error
    assert a.get_program_counter_value() == 0x3200

    # test of invalid input
    with pytest.raises(AssertionError):
        a.set_program_counter_value(-1)

    a.set_program_counter_value(16777216)

    with pytest.raises(AssertionError):
        # 1 beyond the max value
        a.set_program_counter_value(16777216 + 1)

def test_other_registers():
    """
    Test the other registers to ensure that they can read and write properly
    :return:
    """

    a = M68K()

    # test all of the 4 byte registers (32 bit)
    # exclude the program counter due to its restrictions
    normal_registers = [Register.D0, Register.D1, Register.D2, Register.D3, Register.D4, Register.D5, Register.D6,
                        Register.D7, Register.A0, Register.A1, Register.A2, Register.A3, Register.A4, Register.A5,
                        Register.A6, Register.A7]
    for reg in normal_registers:
        _test_single_register(a, reg)


def _test_single_register(sim: M68K, reg: Register):
    """
    Tests a single register
    :param sim:
    :param reg:
    :return:
    """

    # test that the initial value is zero
    assert sim.get_register_value(reg) == 0
    # now try setting a single byte value to the register
    sim.set_register_value(reg, 0xAF)
    # ensure the values are accurate
    assert sim.get_register_value(reg) == 0xAF

    sim.set_register_value(reg, 0xFF)
    assert sim.get_register_value(reg) == 0xFF

    # hasn't died yet (hopefully)
    # so move on to 2 bytes
    sim.set_register_value(reg, 0xBEEF)
    assert sim.get_register_value(reg) == 0xBEEF
    sim.set_register_value(reg, 0xFFFF)
    assert sim.get_register_value(reg) == 0xFFFF

    # 3
    sim.set_register_value(reg, 0xBEEFFE)
    assert sim.get_register_value(reg) == 0xBEEFFE
    sim.set_register_value(reg, 0xFFFFFF)
    assert sim.get_register_value(reg) == 0xFFFFFF

    # set all 4 bytes including max value
    sim.set_register_value(reg, 0xDEADBEEF)
    assert sim.get_register_value(reg) == 0xDEADBEEF
    sim.set_register_value(reg, 0xFFFFFFFF)
    assert sim.get_register_value(reg) == 0xFFFFFFFF

    # mess with out of bounds setting
    with pytest.raises(AssertionError):
        sim.set_register_value(reg, -1)

    with pytest.raises(AssertionError):
        sim.set_register_value(reg, 0xFFFFFFFF + 1)

    # ensure that the resulting value is still accurate after errors
    assert sim.get_register_value(reg) == 0xFFFFFFFF

def test_condition_code_register():
    """
    Test the special case condition code register which is only a single byte
    Also check that the status bits are set and read properly
    :return:
    """

    # the condition code register is a single byte so it cannot be tested like the other
    # registers
    a = M68K()

    # test initial value
    assert a.get_register_value(Register.ConditionCodeRegister) == 0
    assert a.get_register_value(Register.CCR) == 0

    # test setting a value in bounds
    a.set_register_value(Register.CCR, 0xAF)

    # after this can assume that the enums are correctly equal to each other
    assert a.get_register_value(Register.ConditionCodeRegister) == 0xAF
    assert a.get_register_value(Register.CCR) == 0xAF

    # now test invalid input
    with pytest.raises(AssertionError):
        a.set_register_value(Register.CCR, -1)
    with pytest.raises(AssertionError):
        a.set_register_value(Register.CCR, 0xFF + 1)
