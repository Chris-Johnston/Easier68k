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
from .assembly_transformer import Literal

from .opcode_base import OpCodeBase

debug = 0

class OpCodeCmp(OpCodeBase):
    def __init__(self):
        super().__init__()
        self.src_reg = None
        self.src_ea_mode = None
        self.dest_reg = None
        self.dest_ea_mode = None


    def from_param_list(self, size: OpSize, param_list: list):
        super().from_param_list(size, param_list)

        assert len(param_list) == 2, "wrong param list size"

        # TODO: this param list to ea mode logic will get repetitive quick, 
        # need to have a standardized way to do this
        src, dest = param_list

        if isinstance(src, Literal):
            self.src_ea_mode = EAMode.IMM
            self.src_reg = None
        elif isinstance(src, tuple):
            self.src_reg, self.src_ea_mode = src
        else:
            print("src from param list", src)

        if isinstance(dest, Literal):
            self.dest_ea_mode = EAMode.IMM
            self.dest_reg = None
        elif isinstance(dest, tuple):
            self.dest_reg, self.dest_ea_mode = dest
        else:
            print("dest from param list", dest)


    def from_asm_values(self, values: list):
        # register, size, ea mode, ea reg

        dest_reg, size, src_mod, src_reg = values
        self.size = OpSize.from_asm_value(size)

        self.src_ea_mode = EAMode.from_bin_mode(src_mod, src_reg)

        self.src_reg = src_reg
        self.dest_reg = dest_reg
        self.dest_ea_mode = EAMode.DRD


    def to_asm_values(self) -> list:
        # size, dest reg, dest mod, src mode, src reg
        ret_size = self.size.get_asm_value()

        dest_mode, dest_register = self.dest_ea_mode.get_bin_values()
        src_mode, src_register = self.src_ea_mode.get_bin_values()

        x = [self.dest_reg,
            ret_size,
            src_mode,
            src_register or self.src_reg]
        return x

    def execute(self, cpu: M68K):
        # subtracts the source operand from the dest operand
        # and sets the CCR based on the result
        src_val = cpu.get_ea_value(self.src_ea_mode, self.src_reg, self.size)
        dest_val = cpu.get_ea_value(self.dest_ea_mode, self.dest_reg, self.size)

        print("src", src_val, "dest", dest_val)
        print("dest", self.dest_reg, self.dest_ea_mode)
        result, carry, overflow = src_val.sub_unsigned(dest_val)

        # X - not affected
        # N - set if result is negative, cleared otherwise
        # Z - result zero, cleared otherwise
        # V - if overflow occurs
        # C - if carry occurs
        print("CMP", result)
        cpu.set_ccr_reg(None, result.get_negative(), result.get_zero(), overflow, carry)
        cpu.print_debug()


        global debug
        debug += 1
        print('buuuh')
        if debug > 20:
            print("hack", debug)
            cpu.set_ccr_reg(None, True, False, True, None)
            ccr_vals = cpu.get_condition_status_code_flags()
            print(ccr_vals)
        else:
            print('buh', debug)
            # cpu.set_ccr_reg(None, True, False, False, False)
    
    def get_additional_data_length(self):
        return 0