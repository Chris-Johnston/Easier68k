import pytest

from easier68k.simulator.m68k import M68K

def test_program_counter():
    a = M68K()

    assert a.get_program_counter_value() == 0

    a.set_program_counter_value(0x3200)

    assert a.get_program_counter_value() == 0x3200

    # todo include checks for when the program counter value is not valid