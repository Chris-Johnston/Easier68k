"""
Represent the bit masks that are used to get the mode control
bytes
"""

class FloatingPointModeControl():
    PREC = 0b11000000
    RND =  0b00110000
    ROUNDING_PRECISION = 0b11000000
    ROUNDING_MODE = 0b00110000