"""
Represents the bitmasks used to
get the values of bits from the FPCC byte
"""

class FloatingPointConditionCode():
    """
    Represents the bit masks that are used
    to get values from the FPCC
    """
    N = 1 << 27
    Z = 1 << 26
    I = 1 << 25
    NAN = 1 << 24

    NEGATIVE = N
    ZERO = Z
    INFINITY = I
    NOT_A_NUMBER = NAN
    UNORDERED = NAN