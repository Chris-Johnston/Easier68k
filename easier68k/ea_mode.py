"""
Represents an effective addressing mode
and methods associated with it
"""

from typing import Optional
from enum import Enum


class EAMode(Enum):
    # Enum Values

    # Data register direct
    DRD = 0
    # Address register direct
    ARD = 1
    # Address register indirect
    ARI = 2
    # Address register indirect + post increment
    ARIPI = 3
    # Address register indirect + pre decrement
    ARIPD = 4
    # Immediate
    IMM = 5
    # Absolute long address
    ALA = 6
    # Absolute word address
    AWA = 7

    def get_bin_mode(self) -> int:
        # for the most part the enum will match against
        # the binary representation, except for IMM, ALA, AWA
        # since they all are represented the same as 0b111
        if self in [IMM, ALA, AWA]:
            return 0b111
        return self.value

    def get_bin_values(self) -> (int, Optional[int]):
        # gets the mode and register
        mode = self.get_bin_mode()
        if mode == 0b111: # IMM
            return mode, EAModeImmediateRegister.get_register_for_mode(mode)
        return mode, None

    def from_bin_mode(mode: int, register: int): # -> EAMode:
        # converts the mode and register into the EAMode
        if mode == 0b111:
            if register == 0b000:
                return AWA
            elif register == 0b001:
                return ALA
            elif register == 0b100:
                return IMM
        return EAMode(mode)


class EAModeImmediateRegister(Enum):
    REGISTER_IMM = 0b100

    # Absolute long address
    REGISTER_ALA = 0b001

    # Absolute word address
    REGISTER_AWA = 0b000

    def get_register_for_mode(mode: EAMode):
        if mode == EAMode.IMM:
            return REGISTER_IMM
        if mode == EAMode.ALA:
            return REGISTER_ALA
        if mode == EAMode.AWA:
            return REGISTER_AWA
        return None
