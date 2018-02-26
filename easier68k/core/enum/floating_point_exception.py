"""
Defines the different types of floating point exeptions
contains the bit mask used to get their value
"""

class FloatingPointException():
    """
    Represents each of the bit masks used to get these
    values from the register
    """
    BSUN =  0b1000000000000000
    SNAN =  0b0100000000000000
    OPERR = 0b0010000000000000
    OVFL =  0b0001000000000000
    UNFL =  0b0000100000000000
    DZ =    0b0000010000000000
    INEX2 = 0b0000001000000000
    INEX1 = 0b0000000100000000
    BRANCH_SET_ON_UNORDERED = BSUN
    SIGNALING_NOT_A_NUMBER = SNAN
    OPERAND_ERROR = OPERR
    OVERFLOW = OVFL
    UNDERFLOW = UNFL
    DIVIDE_BY_ZERO = DZ
    INEXACT_OPERATION = INEX2
    INEXACT_DECIMAL_INPUT = INEX1
