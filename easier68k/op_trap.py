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

import sys

# need a way to add custom handlers for trap vectors
def trap_code_handler(code: int, cpu: M68K):
    if code == 15:
        # print("TRAP -- 15", file=sys.stderr)
        # todo print out whatever

        # get the task
        reg = Register.D0
        v = cpu.get_register(reg).get_value_unsigned()
        # print(v, file=sys.stderr)
        if v == 14:
            # print out a string
            print('print the string!!')
            print("print: ", end='', file=sys.stderr)
            reg = Register.A1
            addr = cpu.get_register(reg)
            cpu.print_debug()
            while True:
                x = cpu.memory.get(OpSize.WORD, addr)
                addr += 2

                # print(f"{x.get_value_unsigned()} {addr}", file=sys.stderr)
                print(chr(x.get_value_unsigned()), end='', file=sys.stderr)
                if x.get_zero():
                    print("DONE PRINTING THE STRING AAAAA")
                    break
        elif v == 3:
            # display content of D1
            reg = Register.D1
            v = cpu.get_register(reg)
            print(f"TRAP 3: {v.get_value_unsigned()}", file=sys.stderr)

class OpCodeTrap(OpCodeBase):
    def __init__(self):
        super().__init__()
        self.vector = None # 0 - 16 - 4 bytes

    def from_param_list(self, size: OpSize, param_list: list):
        super().from_param_list(size, param_list)

        assert len(param_list) == 1, "wrong param list size"
        self.vector = param_list[0].value

    def from_asm_values(self, values: list):
        self.vector = values[0]

    def to_asm_values(self) -> list:
        return [self.vector]

    def execute(self, cpu: M68K):
        print("TRAP:", self.vector)
        if self.vector == 15:
            trap_code_handler(self.vector, cpu)
    
    def get_additional_data_length(self):
        return 2