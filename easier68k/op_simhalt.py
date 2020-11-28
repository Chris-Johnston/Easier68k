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

class OpCodeSimHalt(OpCodeBase):
    def __init__(self):
        super().__init__()

    def from_param_list(self, size: OpSize, param_list: list):
        super().from_param_list(size, param_list)

    def from_asm_values(self, values: list):
        pass

    def to_asm_values(self) -> list:
        return []

    def execute(self, cpu: M68K):
        print("simahalt")
        cpu.halt()

