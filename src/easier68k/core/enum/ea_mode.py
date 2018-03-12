"""
Represents an effective addressing mode
and methods associated with it
"""

from enum import Enum


class EAMode(Enum):
    # Enum Values

    # Data register direct
    DRD = 0
    DataRegisterDirect = DRD

    # Address register direct
    ARD = 1
    AddressRegisterDirect = ARD

    # Address register indirect
    ARI = 2
    AddressRegisterIndirect = ARI

    # Address register indirect + post increment
    ARIPI = 3
    AddressRegisterIndirectPostIncrement = ARIPI

    # Address register indirect + pre decrement
    ARIPD = 4
    AddressRegisterIndirectPreDecrement = ARIPD

    # Immediate
    IMM = 5
    Immediate = IMM

    # Absolute long address
    ALA = 6
    AbsoluteLongAddress = ALA

    # Absolute word address
    AWA = 7
    AbsoluteWordAddress = AWA
