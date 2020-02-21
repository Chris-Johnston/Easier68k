from abc import ABC, abstractmethod, abstractproperty
from .opcode_assembler import OpCodeAssembler
from .assembly_parameter import AssemblyParameter
from .ea_mode import EAMode
from .ea_mode_bin import EAModeBinary
from .op_size import Size, OpSize
from .m68k import M68K

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
        self.data_register, self.direction, size, _, _ = values
        self.size = Size(size)

    def execute(self, cpu: M68K):
        print("implement ADD you dummy")
        pass

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
