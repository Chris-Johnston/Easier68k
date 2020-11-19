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

from .op_add import OpCodeAdd

class OpCodeOr(OpCodeAdd):
    def __init__(self):
        super().__init__()

    def execute(self, cpu: M68K):
        print("OR")
        ea_mode_value = self._get_ea_mode_value(self.size, cpu)
        reg = cpu.get_register(self.data_register)

        # direction = 1
        # ea V Dn -> Dn
        # direction = 0
        # Dn v ea -> ea
        if self.direction == 1:
            # ea V Dn -> Dn
            final_val = reg | ea_mode_value
            print(f"reg {reg} | result {ea_mode_value} ")
            cpu.set_register(self.data_register, final_value)
        else:
            # Dn v ea -> ea
            final_val = ea_mode_value | reg
            print(f"reg {reg} | result {ea_mode_value} ")
            self._set_ea_mode_value(self.size, cpu, final_val)

        cpu.set_ccr_reg(None, final_val.get_msb(), final_val == 0, 0, 0)
