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
        self.dest_imm = None

    def from_param_list(self, size: OpSize, param_list: list):
        super().from_param_list(size, param_list)

        # param list expected to be of len 2
        assert len(param_list) == 2, "wrong param list size"

        src, dst = param_list
        ea = None

        assert not isinstance(dst, Literal), "DST may not be a literal"

        if isinstance(dst, Register):
            # ea + Dn -> Dn
            # if register is ADDA, technically we have to do some different behavior
            self.direction = 0

            # set the data register num
            # map back into an int
            self.data_register = Register.get_data_register(dst)

            ea = src
        else:
            # Dn + <ea> -> <ea>
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
            self.register = None
            self.dest_imm = ea.value
        elif isinstance(ea, Register):
            if Register.D0 <= ea <= Register.D7:
                self.ea_mode = EAMode.DRD
            elif Register.A0 <= ea <= Register.A7:
                self.ea_mode = EAMode.ARD
            else:
                assert False
            self.register = ea
            # handle indirect, currently the parser doesn't make distinctions
        else:
            print(f"unsupported ea type {type(ea)}")

        # ea + Dn -> Dn
        # or
        # Dn + <ea> -> <ea>
    
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
        self.data_register = self.data_register(data_register_num)

    def to_asm_values(self):
        super_result = super().to_asm_values()

        size = {
            OpSize.BYTE.value: 0b00,
            OpSize.WORD.value: 0b01,
            OpSize.LONG.value: 0b10,
        }[self.size.value]
        data_register_num = Register.get_data_register(self.data_register)

        result = [data_register_num, self.direction, size]
        return result + super_result

    def execute(self, cpu: M68K):

        assert isinstance(self.data_register, Register), "data reg is not Register"
        # get the value
        result = self._get_ea_mode_value(self.size, cpu)
        
        # get the register value
        reg = cpu.get_register(self.data_register)
        
        # add them based on direction
        if self.direction == 1:
            # store in ea
            # final_val = result + reg
            final_val, carry, overflow = result.add_unsigned(reg)
            self._set_ea_mode_value(self.size, cpu, final_val)
        else:
            # store in dn
            # final_val = reg + result
            final_val, carry, overflow = reg.add_unsigned(result)
            
            # map data_register back to the type
            cpu.set_register(self.data_register, final_val)

        cpu.set_ccr_reg(None, final_val.get_msb(), final_val == 0, result.get_msb() != final_val.get_msb(), carry)
    
    def get_immediates(self):
        if self.dest_imm is not None:
            yield self.dest_imm
    
    def set_immediates(self, immediates: list):
        self.dest_imm = immediates[0]
