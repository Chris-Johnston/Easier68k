"""
Represents all of the different conditions
and their corresponding bit values
"""

from enum import Enum


class Condition(Enum):
    # True
    T = 0b0000
    # False
    F = 0b0001
    # Higher
    HI = 0b0010
    # Lower or Same
    LS = 0b0011
    # Carry Clear
    CC = 0b0100
    # Cary Set
    CS = 0b0101
    # Not Equal
    NE = 0b0110
    # Equal
    EQ = 0b0111
    # Overflow Clear
    VC = 0b1000
    # Overflow Set
    VS = 0b1001
    # Plus
    PL = 0b1010
    # Minus
    MI = 0b1011
    # Greater or Equal
    GE = 0b1100
    # Less Than
    LT = 0b1101
    # Greater Than
    GT = 0b1110
    # Less or Equal
    LE = 0b1111

    # could add the mnemonic aliases to this if we wanted
