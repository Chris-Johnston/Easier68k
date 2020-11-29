"""
Represents an effective addressing mode
and methods associated with it
"""

from typing import Optional
from enum import Enum

from .register import Register

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

    def get_bin_mode(self):
        # for the most part the enum will match against
        # the binary representation, except for IMM, ALA, AWA
        # since they all are represented the same as 0b111
        if self in [self.IMM, self.ALA, self.AWA]:
            return self.IMM
        return self

    def get_bin_values(self) -> (int, Optional[int]):
        # gets the mode and register
        mode = self.get_bin_mode()
        if mode == self.IMM: # IMM
            return 0b111, EAModeImmediateRegister.get_register_for_mode(mode).value
        return mode.value, None

    def from_bin_mode(mode: int, register: int): # -> EAMode:
        # converts the mode and register into the EAMode
        if mode == 0b111:
            if register == 0b000:
                return EAMode.AWA
            elif register == 0b001:
                return EAMode.ALA
            elif register == 0b100:
                return EAMode.IMM
        return EAMode(mode)

class EAModeImmediateRegister(Enum):
    REGISTER_IMM = 0b100

    # Absolute long address
    REGISTER_ALA = 0b001

    # Absolute word address
    REGISTER_AWA = 0b000

    def get_register_for_mode(mode: EAMode):
        if mode == EAMode.IMM:
            return EAModeImmediateRegister.REGISTER_IMM
        if mode == EAMode.ALA:
            return EAModeImmediateRegister.REGISTER_ALA
        if mode == EAMode.AWA:
            return EAModeImmediateRegister.REGISTER_AWA
        return None
