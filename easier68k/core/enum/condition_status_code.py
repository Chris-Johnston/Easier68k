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
    X = 0
    N = 1
    Z = 2
    V = 3
    C = 4
    # duplicate human readable names
    Extend = 0
    Negative = 1
    Zero = 2
    Overflow = 3
    Carry = 4
