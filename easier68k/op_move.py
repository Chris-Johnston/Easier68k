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

class OpCodeMove(OpCodeBase): # todo: this file is getting very long quick and will be very annoying to maintain
    def __init__(self):
        super().__init__()

    def to_asm_values(self) -> list:
        pass

    # todo: should find all of these that are similar and make them standard utils
    # that I'm actually aware of
    def _asm_get_size(size: int) -> OpSize:
        if size == 0b01: return OpSize.BYTE
        elif size == 0b11: return OpSize.WORD
        elif size == 0b10: return OpSize.LONG

    def _asm_get_ea(self, reg: int, mode: int): # -> EAMode, Optional[OpSize]:
        if mode == 0b000:
            return EAMode.DRD, Register.get_data_register(reg)
        if mode == 0b001:
            return EAMode.ARD, Register.get_addr_register(reg)
        if mode == 0b010:
            return EAMode.ARI, Register.get_addr_register(reg)
        if mode == 0b011:
            return EAMode.ARIPI, Register.get_addr_register(reg)
        if mode == 0b100:
            return EAMode.ARIPD, Register.get_addr_register(reg)
        if mode == 0b111:
            if register == 0b000:
                return EAMode.AWA, None
            if register == 0b001:
                return EAMode.ALA, None
            if register == 0b100:
                return EAMode.IMM, None
        
    def from_asm_values(self, values):
        # size, dest reg, dest mod, src mode, src reg
        # need to assert the types of src and dest to prevent invalid states
        size, dest_reg, dest_mod, src_mod, src_reg = values
        self.size = OpSize.from_asm_value(size) # self._asm_get_size(size)

        self.dest_ea_mode = EAMode.from_bin_mode(dest_mod, dest_reg)
        self.src_ea_mode = EAMode.from_bin_mode(src_mod, src_reg)

        self.src_reg = src_reg
        self.dest_reg = dest_reg
    
    def from_param_list(self, size: OpSize, values: list):
        pass

    def to_asm_values(self) -> list:
        # size, dest reg, dest mod, src mode, src reg
        ret_size = self.size.get_asm_value()

        dest_mode, dest_register = self.dest_ea_mode.get_bin_values()
        src_mode, src_register = self.src_ea_mode.get_bin_values()

        return [ret_size,
            dest_register or self.dest_reg,
            dest_mode,
            src_mode,
            src_register or self.src_reg]


    def execute(self, cpu: M68K):
        print("MOVE")
        