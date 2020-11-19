"""
Register Enum
Represents the different types of registers
"""

from enum import IntEnum

class Register(IntEnum):
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

    def get_data_register(register_num: int):# -> Register:
        if register_num == 0: return D0
        if register_num == 1: return D1
        if register_num == 2: return D2
        if register_num == 3: return D3
        if register_num == 4: return D4
        if register_num == 5: return D5
        if register_num == 6: return D6
        if register_num == 7: return D7
        return None

    def get_addr_register(register_num: int): # -> Register:
        if register_num == 0: return A0
        if register_num == 1: return A1
        if register_num == 2: return A2
        if register_num == 3: return A3
        if register_num == 4: return A4
        if register_num == 5: return A5
        if register_num == 6: return A6
        if register_num == 7: return A7
        return None

    def get_register_num(self):
        # the smart and clean thing to do would be just to subtract the value
        if self == A0: return 0
        if self == D0: return 0
        if self == A1: return 1
        if self == D1: return 1
        if self == A2: return 2
        if self == D2: return 2
        if self == A3: return 3
        if self == D3: return 3
        if self == A4: return 4
        if self == D4: return 4
        if self == A5: return 5
        if self == D5: return 5
        if self == A6: return 6
        if self == D6: return 6
        if self == A7: return 7
        if self == D7: return 7

# constants that group together the registers
DATA_REGISTERS = [Register.D0, Register.D1, Register.D2, Register.D3,
                  Register.D4, Register.D5, Register.D6, Register.D7]

# all of the An registers
ADDRESS_REGISTERS = [Register.A0, Register.A1, Register.A2, Register.A3,
                     Register.A4, Register.A5, Register.A6, Register.A7]

# all of the address registers, incluing PC
ALL_ADDRESS_REGISTERS = [Register.A0, Register.A1, Register.A2, Register.A3,
                         Register.A4, Register.A5, Register.A6, Register.A7,
                         Register.PC]

# all of the 32 bit registers
FULL_SIZE_REGISTERS = [Register.D0, Register.D1, Register.D2, Register.D3, Register.D4,
                       Register.D5, Register.D6, Register.D7, Register.A0, Register.A1,
                       Register.A2, Register.A3, Register.A4, Register.A5, Register.A6,
                       Register.A7, Register.PC]
