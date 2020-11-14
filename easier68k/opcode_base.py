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

# bytes -> assembler tree find match -> add assembler
# add assembler -> add opcode -> execute

class OpCodeBase():

    # @abstractmethod
    def from_param_list(self, size: OpSize, values: list):
        """
        Initializes the opcode from the parameters provided.
        """
        self.size = size

    @abstractmethod
    def from_asm_values(self, values: list):
        """
        Initializes the opcode from the assembly values.
        """
        pass

    @abstractmethod
    def to_asm_values(self):
        """
        Gets the assembly values for the current state of the opcode,
        so that it can be passed on to the corresponding "assembler/disassembler" type,
        and so that the binary value can be created.
        """
        pass
    
    @abstractmethod
    def execute(self, cpu: M68K):
        pass

class DynamicAddressingModeOpCodeBase(OpCodeBase):
    """
    Base class which implements getting the addressing mode and register (if applicable).

    This assumes that the last two assembly parameters are M (mode) and Xn (register).
    """
    def __init__(self):
        self.ea_mode = None
        self.register = None

        # used for fast lookup
        self._ea_mode_lookup = {
            EAModeBinary.MODE_DRD: EAMode.DRD,
            EAModeBinary.MODE_ARD: EAMode.ARD,
            EAModeBinary.MODE_ARI: EAMode.ARI,
            EAModeBinary.MODE_ARIPI: EAMode.ARIPI,
            EAModeBinary.MODE_ARIPD: EAMode.ARIPD,
            # not worring about Address with Displacement or Address with Index for now
        }

        self._ea_imm_lookup = {
            0b000: EAMode.AWA,
            0b001: EAMode.ALA,
            0b100: EAMode.IMM,
        }

    @abstractmethod
    def to_asm_values(self) -> list:
        # we can return the last two values from this list
        print(self.ea_mode)
        print(EAMode(self.ea_mode))

        mode = {
            EAMode.AWA: 0b000,
            EAMode.ALA: 0b001,
            EAMode.IMM: 0b100,
            EAMode.DRD: EAModeBinary.MODE_DRD,
            EAMode.ARD: EAModeBinary.MODE_ARD,
            EAMode.ARI: EAModeBinary.MODE_ARI,
            EAMode.ARIPI: EAModeBinary.MODE_ARIPI,
            EAMode.ARIPD: EAModeBinary.MODE_ARIPD,
        }[self.ea_mode]
        register = self.register or 0
        return [mode, register]

    @abstractmethod
    def from_asm_values(self, values: list):
        # subclasses of this should implement handling the rest of the values
        # this class will assume that the only relvant ones here are the last two
        mode, register = values[-2:]
        
        if mode == EAModeBinary.MODE_IMM:
            # could be IMM, AWA, ALA, based on register (which isn't a register)
            self.ea_mode = self._ea_imm_lookup[register]
            # do NOT use a register
            self.register = None
        else:
            # register is a register, and just use a look-up
            self.ea_mode = self._ea_mode_lookup[mode]
            self.register = register

    def __get_address(self, size: Size, cpu: M68K) -> MemoryValue:
        """
        Gets the address register to use for 
        ARI, ARIPI, ARIPD
        """
        if self.ea_mode in [
            EAMode.ARI,
            EAMode.ARIPI,
            EAMode.ARIPD,
        ]:
            # handle ARI
            address_register = {
                0: Register.A0,
                1: Register.A1,
                2: Register.A2,
                3: Register.A3,
                4: Register.A4,
                5: Register.A5,
                6: Register.A6,
                7: Register.A7,
            }[self.register]

            # lint: see if I can re-use this code
            if self.ea_mode == EAMode.ARI:
                address = cpu.get_register(address_register)
            elif self.ea_mode == EAMode.ARIPI:
                address = cpu.get_register(address_register)
                # increment the register
                new_address = MemoryValue(len= OpSize.WORD, unsigned_int= OpSize.WORD.value + address.get_value_unsigned())
                cpu.set_register(address_register, new_address)
            elif self.ea_mode == EAMode.ARIPD:
                old_address = cpu.get_register(address_register)
                # increment the reigster
                address = MemoryValue(len= OpSize.WORD, unsigned_int= OpSize.WORD.value + old_address.get_value_unsigned())
                cpu.set_register(address_register, address)
            return address
        else:
            return None

    def _get_IMM_address(self, size: Size, cpu: M68K) -> MemoryValue:
        """
        gets the memory value of the address of the IMM data. makes it easier to get IMM data/address
        """
        address = cpu.get_register(Register.PC).get_value_unsigned() + OpSize.WORD.value
        return MemoryValue(size, unsigned_int=address)

    def _set_ea_mode_value(self, size: Size, cpu: M68K, value: MemoryValue):
        """
        uses the ea_mode and register to set a new value
        """

        # see page 4-6
        # only memory alterable ea_modes are used here
        # cannot use drd

        assert self.ea_mode != EAMode.IMM, "This doesn't make sense?"
        assert self.ea_mode not in [
            EAMode.DRD, EAMode.ARD
        ], "These are not valid modes for setting the value"

        if self.ea_mode in [
            EAMode.ARI,
            EAMode.ARIPI,
            EAMode.ARIPD,
        ]:
            # get the address
            adr = self.__get_address(size, cpu)
            cpu.memory.set(self.size, adr.get_value_unsigned(), value)

        if self.ea_mode == EAMode.ALA or self.ea_mode == EAMode.AWA:
            # get the address following the PC
            # set the value at that address
            imm_size = OpSize.WORD if self.ea_mode == EAMode.AWA else OpSize.LONG
            addr = self._get_IMM_address(OpSize.WORD, cpu).get_value_unsigned()
            print(f"addr {addr:x} value {value}")
            # cpu.memory.set(self.size, addr, value)
            addr = cpu.memory.get(OpSize.WORD, addr).get_value_unsigned()
            cpu.memory.set(imm_size, addr, value)

    def _get_ea_mode_value(self, size: OpSize, cpu: M68K) -> MemoryValue:
        """
        Uses the ea_mode and register to get the value specified.
        TODO should also create one to set the value
        """
        if self.ea_mode == EAMode.IMM:
            # get value at PC + 2 (word)
            imm_location = cpu.get_register(Register.PC).get_value_unsigned() + OpSize.WORD.value
            return cpu.memory.get(self.size, imm_location)

        if self.ea_mode == EAMode.DRD:
            # Direct, so look up the location from the register
            # then return the value at that location            
            # TODO move this to the class so this doesn't have to be instantiated each time
            data_register = {
                0: Register.D0,
                1: Register.D1,
                2: Register.D2,
                3: Register.D3,
                4: Register.D4,
                5: Register.D5,
                6: Register.D6,
                7: Register.D7,
            }[self.register]
            return cpu.get_register(data_register)

        if self.ea_mode in [EAMode.ARIPI, EAMode.ARIPD, EAMode.ARI]:
            address_register = {
                0: Register.A0,
                1: Register.A1,
                2: Register.A2,
                3: Register.A3,
                4: Register.A4,
                5: Register.A5,
                6: Register.A6,
                7: Register.A7,
            }[self.register]

            if self.ea_mode == EAMode.ARI:
                address = cpu.get_register(address_register)
            elif self.ea_mode == EAMode.ARIPI:
                address = cpu.get_register(address_register)
                # increment the register
                new_address = MemoryValue(len= OpSize.WORD, unsigned_int= OpSize.WORD.value + address.get_value_unsigned())
                cpu.set_register(address_register, new_address)
            elif self.ea_mode == EAMode.ARIPD:
                old_address = cpu.get_register(address_register)
                # increment the reigster
                address = MemoryValue(len= OpSize.WORD, unsigned_int= OpSize.WORD.value + old_address.get_value_unsigned())
                cpu.set_register(address_register, address)

            return cpu.memory.get(self.size, address.get_value_unsigned())
        
        if self.ea_mode in [EAMode.ALA, EAMode.AWA]:
            # TODO handle distinction between long and word here
            imm_location = cpu.get_register(Register.PC).get_value_unsigned() + OpSize.WORD.value
            address = MemoryValue(self.size, unsigned_int=imm_location)
            location = cpu.memory.get(self.size, address).get_value_unsigned()
            return cpu.memory.get(self.size, location)
        
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
            self.data_register = { # this should be part of add, oops
                0: Register.D0,
                1: Register.D1,
                2: Register.D2,
                3: Register.D3,
                4: Register.D4,
                5: Register.D5,
                6: Register.D6,
                7: Register.D7,
            }[dst]

            ea = src
        else:
            # Dn + <ea> -> <ea>
            print("Dn + ea -> ea")
            self.direction = 1
            ea = dst

            # with confidence I can say that 90% of this code has
            # written between the hours of 8 PM and 2 AM
            self.data_reg = { # this should be part of add, oops
                0: Register.D0,
                1: Register.D1,
                2: Register.D2,
                3: Register.D3,
                4: Register.D4,
                5: Register.D5,
                6: Register.D6,
                7: Register.D7,
            }[src]
        
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
        self.data_register = {
                0: Register.D0,
                1: Register.D1,
                2: Register.D2,
                3: Register.D3,
                4: Register.D4,
                5: Register.D5,
                6: Register.D6,
                7: Register.D7,
            }[data_register_num]

    def to_asm_values(self):
        super_result = super().to_asm_values()

        size = {
            OpSize.BYTE.value: 0b00,
            OpSize.WORD.value: 0b01,
            OpSize.LONG.value: 0b10,
        }[self.size.value]

        print("data reg", self.data_register)
        data_register_num = {
            Register.D0: 0,
            Register.D1: 1,
            Register.D2: 2,
            Register.D3: 3,
            Register.D4: 4,
            Register.D5: 5,
            Register.D6: 6,
            Register.D7: 7,
        }[self.data_register]

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

    def _asm_get_ea(self, reg: int, mode: int) -> EAMode, Optional[OpSize]:
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
        self.size = self._asm_get_size(size)
        self.dest_ea_mode, self.dest_size = self._asm_get_size(dest_reg, dest_mod)
        self.src_ea_mode, self.src_size = self._asm_get_size(src_reg, src_mod)
    
    def from_param_list(self, values):
        pass

    def to_asm_values(self):
        pass

    def execute(self, cpu: M68K):
        print("MOVE")
        

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

class OpCodeAnd(OpCodeAdd):
    def __init__(self):
        super().__init__()

    def execute(self, cpu):
        print("AND")
        ea_val = self._get_ea_mode_value(self.size, cpu)
        # get the register value
        dn_val = cpu.get_register(self.data_register)
        carry = 0 # TODO
        
        if self.direction == 1:
            # ea - Dn -> ea
            final_val = ea_val & dn_val
            print(f"1 storing {final_val} in ea")
            self._set_ea_mode_value(self.size, cpu, final_val)
        else:
            # Dn - ea -> Dn
            final_val = dn_val & ea_val
            print(f"0 storing {final_val} in dx")
            cpu.set_register(self.data_register, final_val)

        cpu.set_ccr_reg(None, final_val.get_msb(), final_val == 0, 0, 0)

# add more types by adding to this dict
OPCODE_LOOKUP = {
    "add": OpCodeAdd,
    "or": OpCodeOr,
    "sub": OpCodeSub,
    "and": OpCodeAnd,
    "move": OpCodeMove
}

def get_opcode(opcode_name: str, asm_values: list) -> OpCodeBase:
    assert opcode_name in OPCODE_LOOKUP, f"{opcode_name} is not yet implemented"

    op = OPCODE_LOOKUP[opcode_name]()
    op.from_asm_values(asm_values)
    return op

def get_opcode_parsed(opcode_name: str, size: OpSize, param_list: list) -> OpCodeBase:
    assert opcode_name in OPCODE_LOOKUP, f"{opcode_name} is not yet implemented"

    op = OPCODE_LOOKUP[opcode_name]()
    print("param list", param_list)
    op.from_param_list(size, param_list)

    return op
