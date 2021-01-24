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
debug = 0

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
        # if size == 0b11 indicates that this is a memory shift
        # which means we only care about the ea
        assert size != 3, "Memory shift is not supported yet, support for multiple formats is not implemented"
        self.size = OpSize(size)
        self.ir = ir
        self.register = Register.get_data_register(register)

    def to_asm_values(self) -> list:
        return [
            self.count_register,
            self.size.get_other_asm_value(),
            self.ir,
            self.register.get_register_num()
        ]

    def execute(self, cpu: M68K):
        # load the effective address into the specified address register
        # all 32 bits of the address register are affected by this instruction
        shift_amount = 0
        if self.ir == 0:
            shift_amount = self.count_register
        else:
            amount_reg = Register.get_data_register(self.count_register)
            shift_amount = cpu.get_register(amount_reg).get_value_unsigned() % 64

        dest_register = self.register
        original_value = cpu.get_ea_value(EAMode.DRD, dest_register)
        
        if shift_amount == 0:
            cpu.set_ccr_reg(None, False, False, False, False)

        if self.shift_right:
            # shift right
            high_bit = original_value.get_msb()
            v = original_value.get_value_unsigned()

            shifted_out = 0
            # there is probably a better way to do this
            for _ in range(shift_amount):
                shifted_out = v & 1
                v = v >> 1
                # set the high bit if originally set
                if high_bit == 1:
                    mask_bytes = original_value.get_size().get_number_of_bytes()
                    v |= 1 << (mask_bytes * 8 - 1)
            carry_extend = shifted_out != 0
            mv = MemoryValue(self.size, unsigned_int=v)

            cpu.set_register(dest_register, mv)
            # overflow is always false since the high bit is preserved
            cpu.set_ccr_reg(carry_extend, mv.get_negative(), mv.get_zero(), False, carry_extend)
        else:
            # shift left
            high_bit = original_value.get_msb()
            v = original_value.get_value_unsigned() 
            v = v << shift_amount
            mv = MemoryValue(self.size, unsigned_int=v)
            new_high_bit = mv.get_msb()
            overflow = new_high_bit != high_bit
            carry_extend = high_bit != 0

            assert v != 0
            cpu.set_register(dest_register, mv)
            cpu.set_ccr_reg(carry_extend, mv.get_negative(), mv.get_zero(), overflow, carry_extend)
    
    def get_immediates(self):
        # literal data field is not immediate but is instead a field of the op itself
        return []

    def set_immediates(self):
        pass

class OpCodeAsl(OpCodeArithmeticShiftBase):
    def __init__(self):
        super().__init__(False)

class OpCodeAsr(OpCodeArithmeticShiftBase):
    def __init__(self):
        super().__init__(True)