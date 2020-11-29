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

class OpCodeMove(OpCodeBase):
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
        print("move param list", param_list)

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

        print("alkjdsf", src, dest, self.src_reg, self.src_ea_mode)

    def from_asm_values(self, values: list):
        # size, dest reg, dest mod, src mode, src reg
        # need to assert the types of src and dest to prevent invalid states
        size, dest_reg, dest_mod, src_mod, src_reg = values
        self.size = OpSize.from_asm_value(size)

        self.dest_ea_mode = EAMode.from_bin_mode(dest_mod, dest_reg)
        self.src_ea_mode = EAMode.from_bin_mode(src_mod, src_reg)

        self.src_reg = src_reg
        self.dest_reg = dest_reg

    def to_asm_values(self) -> list:
        # size, dest reg, dest mod, src mode, src reg
        ret_size = self.size.get_asm_value()

        dest_mode, dest_register = self.dest_ea_mode.get_bin_values()
        src_mode, src_register = self.src_ea_mode.get_bin_values()

        x = [ret_size,
            dest_register or self.dest_reg,
            dest_mode,
            src_mode,
            src_register or self.src_reg]
        print("to asm values", x)
        return x


    def execute(self, cpu: M68K):
        print('eeeeeeeeeeeeeeee')
        print("moving", self.src_reg, self.src_ea_mode)
        # move data from source to destination
        src_val = cpu.get_ea_value(self.src_ea_mode, self.src_reg, self.size)
        print("val", src_val)
        print("into", self.dest_ea_mode, self.dest_reg)
        cpu.set_ea_value(self.dest_ea_mode, self.dest_reg, src_val, self.size)
        # X - not affected
        # N - set if result is negative, cleared otherwise
        # Z - result zero, cleared otherwise
        # V - cleared
        # C - cleared
        cpu.set_ccr_reg(None, src_val.get_negative(), src_val.get_zero(), False, False)
    
    def get_additional_data_length(self):
        v = 0
        if self.src_ea_mode in [EAMode.IMM, EAMode.ALA, EAMode.AWA]:
            v += 2
        if self.dest_ea_mode in [EAMode.IMM, EAMode.ALA, EAMode.AWA]:
            v += 2
        print("MOV increment by", v)
        return v