# Conversion utils

def get_number_of_bytes(byte_char: str) -> int:
    """

    B is a single byte

    >>> get_number_of_bytes('B')
    1

    >>> get_number_of_bytes('b')
    1

    >>> get_number_of_bytes('W')
    2

    >>> get_number_of_bytes('w')
    2

    >>> get_number_of_bytes('L')
    4

    >>> get_number_of_bytes('l')
    4

    Invalid input tests are in the pytest

    Converts the byte character into the number of bytes
    for that length of value
    :param byte_char:
    :return:
    """
    assert isinstance(byte_char, str)

    byte_char = byte_char.upper()

    if byte_char == 'B':
        return 1
    if byte_char == 'W':
        return 2
    if byte_char == 'L':
        return 4

    raise ValueError('The input was not a valid byte length character.')


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
