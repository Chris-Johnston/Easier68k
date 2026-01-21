from easier68k import TrapVector
import pytest

def test_trap_vector_parse():

    with pytest.raises(AssertionError):
        TrapVector.parse('-100')

    with pytest.raises(AssertionError):
        TrapVector.parse('#100')

    a = TrapVector.parse('#15')
    assert a.value == 15

    a = TrapVector.parse('#%1110')
    assert a.value == 14