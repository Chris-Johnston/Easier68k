from abc import ABC, abstractmethod, abstractproperty
from .opcode_assembler import OpCodeAssembler
from .assembly_parameter import AssemblyParameter
from .ea_mode import EAMode
from .ea_mode_bin import EAModeBinary
from .op_size import Size, OpSize
from .m68k import M68K
from .register import Register
from .memory_value import MemoryValue

# bytes -> assembler tree find match -> add assembler
# add assembler -> add opcode -> execute

class OpCodeBase():

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
            EAModeBinary.MODE_DRD: EAMode.DataRegisterDirect,
            EAModeBinary.MODE_ARD: EAMode.AddressRegisterDirect,
            EAModeBinary.MODE_ARI: EAMode.AddressRegisterIndirect,
            EAModeBinary.MODE_ARIPI: EAMode.AddressRegisterIndirectPostIncrement,
            EAModeBinary.MODE_ARIPD: EAMode.AddressRegisterIndirectPreDecrement,
            # not worring about Address with Displacement or Address with Index for now
        }

        self._ea_imm_lookup = {
            0b000: EAMode.AbsoluteWordAddress,
            0b001: EAMode.AbsoluteLongAddress,
            0b100: EAMode.Immediate,
        }

    @abstractmethod
    def execute(self, cpu: M68K):
        pass

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
            EAMode.AddressRegisterIndirect,
            EAMode.AddressRegisterIndirectPostIncrement,
            EAMode.AddressRegisterIndirectPreDecrement,
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
            if self.ea_mode == EAMode.AddressRegisterIndirect:
                address = cpu.get_register(address_register)
            elif self.ea_mode == EAMode.AddressRegisterIndirectPostIncrement:
                address = cpu.get_register(address_register)
                # increment the register
                new_address = MemoryValue(len= OpSize.WORD, unsigned_int= OpSize.WORD.value + address.get_value_unsigned())
                cpu.set_register(address_register, new_address)
            elif self.ea_mode == EAMode.AddressRegisterIndirectPreDecrement:
                old_address = cpu.get_register(address_register)
                # increment the reigster
                address = MemoryValue(len= OpSize.WORD, unsigned_int= OpSize.WORD.value + old_address.get_value_unsigned())
                cpu.set_register(address_register, address)
            return address
        else:
            return None

    def _get_immediate_address(self, size: Size, cpu: M68K) -> MemoryValue:
        """
        gets the memory value of the address of the immediate data. makes it easier to get IMM data/address
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

        assert self.ea_mode != EAMode.Immediate, "This doesn't make sense?"
        assert self.ea_mode not in [
            EAMode.DRD, EAMode.AddressRegisterDirect
        ], "These are not valid modes for setting the value"

        if self.ea_mode in [
            EAMode.AddressRegisterIndirect,
            EAMode.AddressRegisterIndirectPostIncrement,
            EAMode.AddressRegisterIndirectPreDecrement,
        ]:
            # get the address
            adr = self.__get_address(size, cpu)
            cpu.memory.set(self.size, adr.get_value_unsigned(), value)

        if self.ea_mode == EAMode.AbsoluteLongAddress or self.ea_mode == EAMode.AbsoluteWordAddress:
            # get the address following the PC
            # set the value at that address
            imm_size = OpSize.WORD if self.ea_mode == EAMode.AbsoluteWordAddress else OpSize.LONG
            addr = self._get_immediate_address(OpSize.WORD, cpu).get_value_unsigned()
            print(f"addr {addr:x} value {value}")
            # cpu.memory.set(self.size, addr, value)
            addr = cpu.memory.get(OpSize.WORD, addr).get_value_unsigned()
            cpu.memory.set(imm_size, addr, value)


    def _get_ea_mode_value(self, size: OpSize, cpu: M68K) -> MemoryValue:
        """
        Uses the ea_mode and register to get the value specified.
        TODO should also create one to set the value
        """
        if self.ea_mode == EAMode.Immediate:
            # get value at PC + 2 (word)
            imm_location = cpu.get_register(Register.PC).get_value_unsigned() + OpSize.WORD.value
            return cpu.memory.get(self.size, imm_location)

        if self.ea_mode == EAMode.DataRegisterDirect:
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

        if self.ea_mode in [EAMode.AddressRegisterIndirectPostIncrement, EAMode.AddressRegisterIndirectPreDecrement, EAMode.AddressRegisterIndirect]:
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

            if self.ea_mode == EAMode.AddressRegisterIndirect:
                address = cpu.get_register(address_register)
            elif self.ea_mode == EAMode.AddressRegisterIndirectPostIncrement:
                address = cpu.get_register(address_register)
                # increment the register
                new_address = MemoryValue(len= OpSize.WORD, unsigned_int= OpSize.WORD.value + address.get_value_unsigned())
                cpu.set_register(address_register, new_address)
            elif self.ea_mode == EAMode.AddressRegisterIndirectPreDecrement:
                old_address = cpu.get_register(address_register)
                # increment the reigster
                address = MemoryValue(len= OpSize.WORD, unsigned_int= OpSize.WORD.value + old_address.get_value_unsigned())
                cpu.set_register(address_register, address)

            return cpu.memory.get(self.size, address.get_value_unsigned())
        
        if self.ea_mode in [EAMode.AbsoluteLongAddress, EAMode.AbsoluteWordAddress]:
            # TODO handle distinction between long and word here
            imm_location = cpu.get_register(Register.PC).get_value_unsigned() + OpSize.WORD.value
            address = MemoryValue(self.size, unsigned_int=imm_location)
            location = cpu.memory.get(self.size, address).get_value_unsigned()
            return cpu.memory.get(self.size, location)
        
class OpCodeAdd(DynamicAddressingModeOpCodeBase):
    """
    Add opcode. Also serves as the base for AND, OR, and SUB, since they all assemble
    in a similar way.
    """
    def __init__(self):
        super().__init__()
        self.data_register = None
        self.direction = None
        self.size = None
    
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

    def execute(self, cpu: M68K):
        print("ADD")

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
            print(f"0 storing {final_val} in dx")
            cpu.set_register(self.data_register, final_val)

        cpu.set_ccr_reg(None, final_val.get_msb(), final_val == 0, result.get_msb() != final_val.get_msb(), carry)

class OpCodeOr(OpCodeAdd):
    def __init__(self):
        super().__init__()

    def execute(self, cpu):
        print("implement OR dumbass")

class OpCodeSub(OpCodeAdd):
    def __init__(self):
        super().__init__()

    def execute(self, cpu):
        print("implement sub dumbass")

class OpCodeAnd(OpCodeAdd):
    def __init__(self):
        super().__init__()

    def execute(self, cpu):
        print("implement AND dumbass")

# add more types by adding to this dict
OPCODE_LOOKUP = {
    "add": OpCodeAdd,
    "or": OpCodeOr,
    "sub": OpCodeSub,
    "and": OpCodeAnd,
}

def get_opcode(opcode_name: str, asm_values: list) -> OpCodeBase:
    assert opcode_name in OPCODE_LOOKUP, "Not yet implemented"

    op = OPCODE_LOOKUP[opcode_name]()
    op.from_asm_values(asm_values)
    return op

# class OpCodeAdd(OpCodeBase): # a lot of opcodes use the M Xn format, so will make another class for that
#     def __init__(self):
#         self.data_operand = None
#         self.ea_operand = None
#         self.op_size = None
#         self.direction = None

#     def from_asm_values(self, values: list):
#         data_register, \
#         self.direction, \
#         op_size, \
#         addressing_mode, ea_register = values

#         # convert the addressing mode to the EAMode enum
#         # TODO make EAMode and EAModeBinary the same thing
#         modes = {
#             EAModeBinary.MODE_DRD: EAMode.DRD,
#             EAModeBinary.MODE_ARD: EAMode.ARD,
#             EAModeBinary.MODE_ARI: EAMode.ARI,
#             EAModeBinary.MODE_ARIPI: EAMode.ARIPI,
#             EAModeBinary.MODE_ARIPD: EAMode.ARIPD,
#             # these are all the same value, will not work
#             # EAModeBinary.MODE_IMM: EAMode.IMM,
#             # EAModeBinary.MODE_ALA: EAMode.ALA,
#             # EAModeBinary.MODE_AWA: EAMode.AWA,
#         }
#         if addressing_mode in modes:
#             addressing_mode = modes[addressing_mode]
#         elif addressing_mode == EAModeBinary.MODE_IMM:
#             # determine this from the ea_register
#             addressing_mode = {
#                 0b000: EAMode.AbsoluteWordAddress,
#                 0b001: EAMode.AbsoluteLongAddress,
#                 0b100: EAMode.Immediate,
#             }[ea_register]

#         self.data_operand = AssemblyParameter(EAMode.DRD, data_register)
#         self.ea_operand = AssemblyParameter(addressing_mode, ea_register)
#         # self.op_size = Size(op_size)
#         # convert the op_size from assembly
#         # into the opsize used everywhere else
#         self.op_size = {
#             0b00: OpSize.BYTE,
#             0b01: OpSize.WORD,
#             0b10: OpSize.LONG,
#         }[op_size]
        
    
#     def execute(self, cpu: M68K):
#         """
#         Adds the source operand to to the destination operand using
#         binary addition and stores the result in the destination location.

#         The size of the operation may be specified as byte, word, or long.
#         The mode of the instruction indicates which operand is the source
#         and which is the dest, as well as operand size.
#         """

#         # get the values

#         if self.direction:
#             # <ea> + Dn -> <ea>
#             self.left_value = self.ea_operand.get_value(cpu, self.op_size)
#             self.right_value = self.data_operand.get_value(cpu, self.op_size)
#             print(f'ea value is {self.left_value}')
#             print(f'right value is {self.right_value}')
#         else:
#             # Dn + <ea> -> Dn
#             self.right_value = self.ea_operand.get_value(cpu, self.op_size)
#             self.left_value = self.data_operand.get_value(cpu, self.op_size)
#             print(f'ea value is {self.left_value}')
#             print(f'right value is {self.right_value}')

#         # https://stackoverflow.com/a/6265950

#         # Overflow flags get set when the register cannot properly represent the result as a signed value (you overflowed into the sign bit).
#         # Carry flags are set when the register cannot properly represent the result as an unsigned value (no sign bit required).

#         # TODO 1/27 working on the ccr
#         # TODO 1/27 work on the overflow
#         result, carry = self.left_value.add_unsigned(self.right_value)
#         print(f'result of addition {result}')

#         # set the value
#         if self.direction:
#             # <ea> + Dn -> <ea>
#             self.ea_operand.set_value(cpu, result)
#         else:
#             # Dn + <ea> -> Dn
#             self.data_operand.set_value(cpu, result)

#         # executing Add
#         cpu.set_ccr_reg(carry, result.get_negative(), result.get_value_unsigned() == 0, None, carry)
