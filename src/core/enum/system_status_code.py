"""
Represents the upper byte of the Status Register
See Fig 1-8
"""

class SystemStatusCode():
    # individual bytes
    I0 = 1 << 8
    I1 = 1 << 9
    I2 = 1 << 10

    # combination, note that this won't be
    # a single bit value
    INTERRUPT_PRIORITY_MASK = I0 | I1 | I2

    M = 1 << 12
    MASTER_STATE = M
    INTERRUPT_STATE = M

    S = 1 << 13
    SUPERVISOR_STATE = S
    USER_STATE = S

    T0 = 1 << 14
    T1 = 1 << 15
    TRACE_ENABLE = T0 | T1


