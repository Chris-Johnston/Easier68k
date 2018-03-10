"""
Register Enum
Represents the different types of registers
"""

from enum import Enum

class Register(Enum):
    # General-Purpose 32-Bit registers
    # Data Registers
    D0 = 0
    D1 = 1
    D2 = 2
    D3 = 3
    D4 = 4
    D5 = 5
    D6 = 6
    D7 = 7
    # Address registers
    A0 = 8
    A1 = 9
    A2 = 10
    A3 = 11
    A4 = 12
    A5 = 13
    A6 = 14
    # User stack pointer
    A7 = 15
    # Program Counter
    PC = 16
    ProgramCounter = 16
    # Condition Code Register (5 bits in the lower byte)
    CCR = 17
    ConditionCodeRegister = 17

# constants that group together the registers
DATA_REGISTERS = [Register.D0, Register.D1, Register.D2, Register.D3,
                  Register.D4, Register.D5, Register.D6, Register.D7]
ADDRESS_REGISTERS = [Register.A0, Register.A1, Register.A2, Register.A3,
                     Register.A4, Register.A5, Register.A6, Register.A7]

# all of the address registers that are limited to fit within the bounds of memory 2^24
MEMORY_LIMITED_ADDRESS_REGISTERS = [Register.A0, Register.A1, Register.A2, Register.A3,
                                    Register.A4, Register.A5, Register.A6, Register.A7,
                                    Register.PC]

# all of the 32 bit registers
FULL_SIZE_REGISTERS = [Register.D0, Register.D1, Register.D2, Register.D3, Register.D4,
                       Register.D5, Register.D6, Register.D7, Register.A0, Register.A1,
                       Register.A2, Register.A3, Register.A4, Register.A5, Register.A6,
                       Register.A7, Register.PC]