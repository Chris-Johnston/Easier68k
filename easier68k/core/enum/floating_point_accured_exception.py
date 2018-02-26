"""
Defines the bit mask used to get the
Accured Exception from the FPSR
"""

class FloatingPointAccuredException():
    IOP = 1 << 7
    OVFL = 1 << 6
    UNFL = 1 << 5
    DZ = 1 << 4
    INEX = 1 << 3

    INVALID_OPERATION = IOP
    OVERFLOW = OVFL
    UNDERFLOW = UNFL
    DIVIDE_BY_ZERO = DZ
    INEXACT = INEX