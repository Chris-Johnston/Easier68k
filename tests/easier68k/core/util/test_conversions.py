import pytest

from src.easier68k.core.util.conversions import word_to_byte, word_to_long

def test_word_to_long():
    assert word_to_long(0) == 0
    assert word_to_long(0x12341234) == 0x1234
    assert word_to_long(0x123412341234) == 0x1234
    assert word_to_long(-1) == -1

    # try invalid input
    with pytest.raises(TypeError, AttributeError):
        word_to_long('invalid')

def test_word_to_byte():
    assert word_to_byte(0) == 0
    assert word_to_byte(0x1234) == 0x34
    assert word_to_byte(0x12341234) == 0x34
    assert word_to_byte(-1) == -1

    # try invalid input
    with pytest.raises(TypeError, AttributeError):
        word_to_byte('invalid')
