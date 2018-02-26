# Conversion utils

def word_to_long(word: int):
    """
    >>> hex(word_to_long(0x12341234))
    '0x1234'

    >>> hex(word_to_long(0))
    '0x0'

    This size should never happen!
    >>> hex(word_to_long(0x123412341))
    '0x2341'

    Masks the given word value to a long
    Also will work with bytes and words
    :param word:
    :return:
    """
    return word & 0x0000FFFF

def word_to_byte(word: int):
    """
    >>> hex(word_to_byte(0x12341234))
    '0x34'

    >>> word_to_byte(257)
    1

    >>> hex(word_to_byte(0x00001111))
    '0x11'

    Masks the given word, long or byte value into a byte
    :param word:
    :return:
    """
    return word & 0xFF