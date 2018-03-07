# Conversion utils


def to_word(word: int) -> int:
    """
    >>> hex(to_word(0x1234ABCD))
    '0xabcd'

    >>> hex(to_word(0))
    '0x0'

    This size should never happen!
    >>> hex(to_word(0x12345678ABCD))
    '0xabcd'

    Masks the given value to the size of a word (16 bits)
    :param word:
    :return:
    """
    assert isinstance(word, int), 'Argument is not of type int'
    return word & 0xFFFF


def to_byte(word: int) -> int:
    """
    >>> hex(to_byte(0x12345678))
    '0x78'

    >>> to_byte(257)
    1

    >>> hex(to_byte(0x00001101))
    '0x1'

    Masks the given value to the size of a byte (8 bits)
    :param word:
    :return:
    """
    assert isinstance(word, int), 'Argument is not of type int'

    return word & 0xFF
