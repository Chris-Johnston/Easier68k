import pytest

from easier68k.simulator.m68k import M68K

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