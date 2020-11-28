from abc import ABC, abstractmethod, abstractproperty
from typing import Optional
from .opcode_assembler import OpCodeAssembler
from .assembly_parameter import AssemblyParameter
from .ea_mode import EAMode
from .ea_mode_bin import EAModeBinary
from .op_size import Size, OpSize
from .m68k import M68K
from .register import Register
from .memory_value import MemoryValue
from .assembly_transformer import Literal, Symbol

from .opcode_base import OpCodeBase

class OpCodeArithmeticShiftBase(OpCodeBase):
    def __init__(self, shift_right: bool):
        super().__init__()
        self.shift_right = shift_right
        self.count_register = None
        self.size = None
        self.ir = None
        self.register = None
        # if only one operand specified, indicates to shift it by 1

    def from_param_list(self, size: OpSize, param_list: list):
        super().from_param_list(size, param_list)

        assert len(param_list) <= 2, "wrong param list size"
        if len(param_list) == 2:
            shift_amount, dest = param_list

            if isinstance(shift_amount, Literal):
                self.count_register = shift_amount.value
                self.ir = 0
            else:
                self.count_register = shift_amount.value
                self.ir = 1

            dest_reg, _ = dest
            self.register = dest_reg
            
        elif len(param_list) == 1:
            reg, mode = param_list[0]
            # if only dest specified, then assume shift by 1
            self.count_register = 1
            self.ir = 0
            self.register = reg

    def from_asm_values(self, values: list):
        # count/register, size, immediate/register, register
        # cr - shift count or register which contains the shift count
        # if ir == 0, contains the shift count where 0 == shift of 8
        # else specifies the data register which contains the shift count % 64
        # register - the register to shift
        cr, size, ir, register = values
        self.count_register = cr
        self.size = OpSize(size)
        self.ir = ir
        self.register = Register.get_data_register(register)

    def to_asm_values(self) -> list:
        return [
            self.count_register,
            self.size.get_asm_value(),
            self.ir,
            self.register.get_register_num()
        ]

    def execute(self, cpu: M68K):
        # load the effective address into the specified address register
        # all 32 bits of the address register are affected by this instruction
        print("TODO ASL ASR exec")

class OpCodeAsl(OpCodeArithmeticShiftBase):
    def __init__(self):
        super().__init__(False)

class OpCodeAsr(OpCodeArithmeticShiftBase):
    def __init__(self):
        super().__init__(True)