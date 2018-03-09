"""
Represents the different condition codes
that are stored in the condition code register
"""


class ConditionStatusCode:
    """
    X - Extend - Set to the value of the C-bit for
    arithmetic operations; otherwise not affected or set
    to a specified result.

    N - Negative - Set if the most significant bit of the
    result is set; otherwise clear.

    Z - Zero - Set if the result equals zero; otherwise
    clear.

    V - Overflow - Set if an arithmetic operation occurs
    implying that the result cannot be represented in the
    operand size; otherwise clear;

    C - Carry - Set if a carry out of the most significant
    bit of the operand occurs for an addition, or if a
    borrow occurs in a subtraction; otherwise clear.
    """

    # these are the masks for the bits in the CCR for each of these values
    X = 0b10000
    N = 0b01000
    Z = 0b00100
    V = 0b00010
    C = 0b00001
    # duplicate human readable names
    Extend = X
    Negative = N
    Zero = Z
    Overflow = V
    Carry = C
