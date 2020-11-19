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

class OpCodeSub(OpCodeAdd):
    def __init__(self):
        super().__init__()

    def execute(self, cpu: M68K):
        print("SUB")
        ea_val = self._get_ea_mode_value(self.size, cpu)
        # get the register value
        dn_val = cpu.get_register(self.data_register)
        carry = 0 # TODO implement carry bit for subtraction
        
        if self.direction == 1:
            # ea - Dn -> ea
            final_val = ea_val.sub_unsigned(dn_val)
            print(f"1 storing {final_val} in ea")
            self._set_ea_mode_value(self.size, cpu, final_val)
        else:
            # Dn - ea -> Dn
            final_val = dn_val.sub_unsigned(ea_val)
            print(f"0 storing {final_val} in dx")
            cpu.set_register(self.data_register, final_val)

        cpu.set_ccr_reg(None, final_val.get_msb(), final_val == 0, ea_val.get_msb() != final_val.get_msb(), carry)
