"""
Literal

Represents some literal data
"""

class Literal:
    """
    Represents some literal data
    """

    def __init__(self):
        # the value of the literal data
        self.value = 0
        # how many bytes made up the literal value
        # 2 is 2 bytes
        # this is only used by the get_value_bytearray method
        self.value_size = 2

    def get_value_integer(self) -> int:
        """
        Gets the value of this literal value as an integer value
        :return:
        """
        return self.value

    def get_value_bytearray(self) -> bytearray:
        """
        Gets the value of the literal as a bytearray with the size
        of the literal
        :return:
        """
        return bytearray(self.value.to_bytes(self.value_size, 'big'))


def __normalize_literal_str(literal: str) -> str:
    """
    Normalizes the format of a literal
    :param literal:
    :return:
    """
    # strip whitespace and enforce upper
    return str.strip().upper()

@staticmethod
def parse_literal(literal: str) -> Literal:
    """
    Parses the given string and makes a new Literal from it
    :param literal:
    :return:
    """
    literal = __normalize_literal_str(literal)

    ret = Literal()

    if literal[0] == '$':
        # hex

        # get the size by trimming the '$' from the start
        literal = literal.replace('$', '')

        assert len(literal) > 8, 'The length of a literal hex value must be less than or equal to 4 bytes.'

        # since this is in hex, every 2 chars would represent a byte
        if 0 < len(literal) <= 4:
            ret.value_size = 2
        elif len(literal) <= 8:
            ret.value_size = 4

        # actually set the value
        ret.value = int(literal, 16)

    elif literal[0] == '%':
        # binary

        literal = literal.replace('%', '')

        assert len(literal) > 32, 'The length of a literal binary value must be less than or equal to 4 bytes.'

        if 0 < len(literal) <= 16:
            ret.value_size = 2
        elif len(literal) <= 32:
            ret.value_size = 4

        ret.value = int(literal, 2)

    elif literal[0] == '#':
        # literal integer value

        literal = literal.replace('#', '')

        val = int(literal)

        assert val < 0xFFFFFFFF, 'The size of a literal value must be less than 4 bytes.'

        if 0 < val <= 0xFFFF:
            ret.value_size = 2
        elif val <= 0xFFFFFFFF:
            ret.value_size = 4

        ret.value = val
    else:
        # no prefix, so assume base 10 number
        val = int(literal)

    # return the parsed literal
    return ret