# Parsing utils


def parse_literal(literal: str):
    """
    Parses a literal (aka "1234" or "$A0F" or "%1001")

    >>> parse_literal('$BA1')
    bytearray(b'\\x0b\\xa1')

    >>> parse_literal('%01010111')
    bytearray(b'W')

    >>> parse_literal('57')
    bytearray(b'9')

    :param literal: A string containing the literal to parse
    :return: The parsed literal (a bytearray type)
    """
    if literal[0] == '$':  # Parsing a hex literal
        if len(literal) % 2 == 0:
            literal = literal[0] + '0' + literal[1:]

        return bytearray.fromhex(literal[1:])
    if literal[0] == '%':  # Parsing a binary literal
        assert (len(literal) - 1) % 4 == 0  # Has to be divisible by 4 to convert into hex
        hexed = hex(int(literal[1:], 2))[2:]
        if len(hexed) % 2 == 1:
            hexed = '0' + hexed

        return bytearray.fromhex(hexed)

    # Integer literal
    return bytearray.fromhex(hex(int(literal))[2:])


