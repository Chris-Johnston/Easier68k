import pytest

from easier68k.core.util.conversions import to_word, to_byte

def test_to_word():
    assert to_word(0) == 0
    assert to_word(0x12345678) == 0x5678
    assert to_word(0x12345678ABCD) == 0xABCD
    assert to_word(-1) == 65535

    # try invalid input
    with pytest.raises((AssertionError, TypeError)):
        to_word('invalid')

def test_to_byte():
    assert to_byte(0) == 0
    assert to_byte(0x1234) == 0x34
    assert to_byte(0x1234ABCD) == 0xCD
    assert to_byte(-1) == 255

    # try invalid input
    with pytest.raises((AssertionError, TypeError)):
        to_byte('invalid')
