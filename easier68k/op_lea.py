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

class OpCodeLea(OpCodeBase):
    def __init__(self):
        super().__init__()
        self.dest_register = None
        self.src_mode = None
        self.src_register = None

    def from_param_list(self, size: OpSize, param_list: list):
        super().from_param_list(size, param_list)

        assert len(param_list) == 2, "wrong param list size"
        src, dest_register = param_list
        print("!!lea params", param_list)

        if isinstance(dest_register, Literal):
            self.dest_register = dest_register.value
        elif isinstance(dest_register, Register):
            self.dest_register = dest_register.value
        elif isinstance(dest_register, tuple):
            reg, mode = dest_register
            self.dest_register = reg
        else:
            print(type(dest_register))
            self.dest_register = dest_register

        # todo param list for this does not seem right
        if isinstance(src, Literal):
            self.src_mode = EAMode.ALA
            self.src_register = src.value
            if isinstance(src.value, Symbol):
                self.src_register = self.src_register.location   
                self.src_mode = EAMode.ALA
        elif isinstance(src, tuple):
            self.src_register, self.src_mode = src
        else:
            print("src from param list", src)


        print("dest reg", self.dest_register, "src mode", self.src_mode, "src reg", self.src_register)

    def from_asm_values(self, values: list):
        # An, src mode, src register
        dest_reg, src_mode, src_register = values
        self.dest_register = Register.get_addr_register(dest_reg)

        self.src_mode = EAMode.from_bin_mode(src_mode, src_register)
        self.src_register = src_register

    def to_asm_values(self) -> list:
        src_mode, src_register = self.src_mode.get_bin_values()
        return [
            self.dest_register.get_register_num(),
            src_mode,
            src_register or self.src_register]

    def execute(self, cpu: M68K):
        # load the effective address into the specified address register
        # all 32 bits of the address register are affected by this instruction

        print(self.dest_register, self.src_mode, self.src_register)
        val = cpu.get_ea_value(self.src_mode, self.src_register)

        print("Lea", val, "into", self.dest_register)
        cpu.set_register(self.dest_register, val)

        pc = cpu.get_program_counter_value()
        cpu.set_program_counter_value(pc + 2)

    def get_additional_data_length(self):
        if self.src_mode in [EAMode.IMM, EAMode.ALA, EAMode.AWA]:
            return 2
        return 0