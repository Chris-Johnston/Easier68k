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

from .op_dynamic_addressing_mode_base import DynamicAddressingModeOpCodeBase

class OpCodeAdd(DynamicAddressingModeOpCodeBase): # should rename this to single dynamic addr
    """
    Add opcode. Also serves as the base for AND, OR, and SUB, since they all assemble
    in a similar way.
    """
    def __init__(self):
        super().__init__()
        self.data_register = None
        self.direction = None
        self.size = None

    def from_param_list(self, size: OpSize, param_list: list):
        super().from_param_list(size, param_list)

        # param list expected to be of len 2
        assert len(param_list) == 2, "wrong param list size"

        src, dst = param_list
        ea = None

        print("params", src, dst)

        assert not isinstance(dst, Literal), "DST may not be a literal"

        if isinstance(dst, Register):
            # ea + Dn -> Dn
            # if register is ADDA, technically we have to do some different behavior
            print("ea + Dn -> Dn (dir 0)")
            self.direction = 0

            # set the data register num
            # map back into an int
            self.data_register = Register.get_data_register(dst)

            ea = src
        else:
            # Dn + <ea> -> <ea>
            print("Dn + ea -> ea")
            self.direction = 1
            ea = dst

            # with confidence I can say that 90% of this code has
            # written between the hours of 8 PM and 2 AM
            self.data_register = Register.get_data_register(src)
        
        # handle the ea
        # currently the parser doesn't do address register indirect or direct
        if isinstance(ea, Literal):
            self.ea_mode = EAMode.IMM
            # todo handle the case of absolute long and abs word addresses
            print("ea is imm")
            self.register = None
        elif isinstance(ea, Register):
            if Register.D0 <= ea <= Register.D7:
                self.ea_mode = EAMode.DRD
            elif Register.A0 <= ea <= Register.A7:
                self.ea_mode = EAMode.ARD
            else:
                print("unsupported register")
                assert False
            self.register = ea
            # handle indirect, currently the parser doesn't make distinctions
            print("ea is reg")
        else:
            print(f"unsupported ea type {type(ea)}")

        print("Add got src", src, "dst", dst)
        print("ea_mode", self.ea_mode, "register", self.register)

        # ea + Dn -> Dn
        # or
        # Dn + <ea> -> <ea>

        print(self.direction, self.register)
    
    def from_asm_values(self, values: list):
        super().from_asm_values(values)
        # Dn D S [M Xn]
        # [M Xn] already covered by DynamicAddressingModeOpCodeBase
        # and are set to ea_mode and register
        data_register_num, self.direction, size, _, _ = values
        # self.size = OpSize(size)
        self.size = {
            0b00: OpSize.BYTE,
            0b01: OpSize.WORD,
            0b10: OpSize.LONG,
        }[size]
        print(f"self size {self.size} size {size}")
        self.data_register = self.data_register(data_register_num)

    def to_asm_values(self):
        super_result = super().to_asm_values()

        size = {
            OpSize.BYTE.value: 0b00,
            OpSize.WORD.value: 0b01,
            OpSize.LONG.value: 0b10,
        }[self.size.value]

        print("data reg", self.data_register)
        data_register_num = Register.get_data_register(self.data_register)

        result = [data_register_num, self.direction, size]
        return result + super_result

    def execute(self, cpu: M68K):

        assert isinstance(self.data_register, Register), "data reg is not Register"
        print("ADD", self.data_register)

        print(f"data register {self.data_register} dir {self.direction} size {self.size}")
        print(f"ea mode {self.ea_mode} register {self.register}")

        # get the value
        result = self._get_ea_mode_value(self.size, cpu)
        print(f"result: {result} size: {self.size}")

        # get the register value
        reg = cpu.get_register(self.data_register)
        print(f"register: {reg}")

        # add them based on direction
        print(f"result size {result.get_size()}")

        if self.direction == 1:
            # store in ea
            # final_val = result + reg
            final_val, carry = result.add_unsigned(reg)
            print(f"1 storing {final_val} in ea")
            self._set_ea_mode_value(self.size, cpu, final_val)
        else:
            # store in dn
            # final_val = reg + result
            final_val, carry = reg.add_unsigned(result)
            print(f"0 storing {final_val} in dx {self.data_register}", self.data_register)
            
            # map data_register back to the type
            cpu.set_register(self.data_register, final_val)

        cpu.set_ccr_reg(None, final_val.get_msb(), final_val == 0, result.get_msb() != final_val.get_msb(), carry)
