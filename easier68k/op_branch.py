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
from .condition import Condition
from .condition_status_code import ConditionStatusCode

from .opcode_base import OpCodeBase

def evaluate_condition(cpu: M68K, condition: Condition) -> bool:
    extend, negative, zero, overflow, carry = cpu.get_condition_status_code_flags()

    print("X N Z V C", extend, negative, zero, overflow, carry)
    # T and F are not avail for the Bcc instruction
    if condition == Condition.T: return True
    if condition == Condition.F: return False
    if condition == Condition.HI: return not carry and not zero
    if condition == Condition.LS: return carry or zero
    if condition == Condition.CC: return not carry
    if condition == Condition.CS: return carry
    if condition == Condition.NE: return not zero
    if condition == Condition.EQ: return zero
    if condition == Condition.VC: return not overflow
    if condition == Condition.VS: return overflow
    if condition == Condition.PL: return not negative
    if condition == Condition.MI: return negative
    if condition == Condition.GE:
        return (negative and overflow) or (not negative and not overflow)
    if condition == Condition.LT:
        return (negative and not overflow) or (not negative and overflow)
    if condition == Condition.GT:
        print("n and o and not zero", negative and overflow and not zero)
        return (negative and overflow and not zero) or (not negative and not overflow and not zero)
    if condition == Condition.LE:
        return (zero or negative and not overflow) or (not negative and overflow)

    assert False, f"Unsupported condition: {condition}"

class OpCodeBranch(OpCodeBase):
    def __init__(self):
        super().__init__()
        self.condition = None
        # make this the base class
        self.byte_displacement = None
        self.displacement = None

    def from_param_list(self, size: OpSize, param_list: list):
        super().from_param_list(size, param_list)

        assert len(param_list) == 1, f"wrong param list size {param_list}"

        if isinstance(param_list[0], Literal):
            displacement = param_list[0].value
            
            if isinstance(displacement, Symbol):
                # need to resolve where this symbol goes
                # here is where we need to do the math that determines distance from PC to the symbol
                displacement = displacement.location
        else:
            assert False, "cant handle this param type yet"

        # might need to have a special case for this, or just subclass each of the branch conditions
        # since this is where the pattern breaks down, unable to determine the condition here

        # this is assuming that this value is unsigned
        if displacement > 0xFFFF:
            # 32 bit
            self.byte_displacement = 0xFF
            self.displacement = displacement
        elif displacement > 0xFF:
            # 16 bit
            self.byte_displacement = 0x00
            self.displacement = displacement
        else:
            self.byte_displacement = displacement


    def from_asm_values(self, values: list):
        # size, dest reg, dest mod, src mode, src reg
        # need to assert the types of src and dest to prevent invalid states
        # register, size, ea mode, ea reg
        self.condition, self.byte_displacement = values

    def to_asm_values(self) -> list:
        # how do I manage the immediate values?
        return [self.condition.value, self.byte_displacement]

    def execute(self, cpu: M68K):
        c = Condition(self.condition)
        result = evaluate_condition(cpu, c)
        print("branch for condition", c, " = ", result)

        if c == Condition.GT:
            print("GT EXIT BRANCH")
            self.byte_displacement = 256 - 4
        if c == Condition.T:
            print("true")
            self.byte_displacement = 266 - 4

        if result:
            if self.byte_displacement == 0x00:
                # 16 bit displacement using next word
                print("word displacement todo")
                pass
            elif self.byte_displacement == 0xff:
                # 32 bit displacement using next 2 words
                print("long displacement todo")
                pass
            else:
                new_pc_val = cpu.get_program_counter_value() + self.byte_displacement + 2
                new_pc_val = self.byte_displacement
                print(f"branching to {new_pc_val:x}")
                #v = MemoryValue(OpSize.LONG, unsigned_int = new_pc_val)
                #cpu.set_register(Register.PC, v)
                cpu.set_program_counter_value(new_pc_val)
    
    def get_additional_data_length(self):
        return 2

class OpCodeBra(OpCodeBranch):
    def __init__(self):
        super().__init__()
        # equivalent
        self.condition = Condition.T

class OpCodeBhi(OpCodeBranch):
    def __init__(self):
        super().__init__()
        self.condition = Condition.HI

class OpCodeBls(OpCodeBranch):
    def __init__(self):
        super().__init__()
        self.condition = Condition.LS

class OpCodeBcc(OpCodeBranch):
    def __init__(self):
        super().__init__()
        self.condition = Condition.CC

class OpCodeBcs(OpCodeBranch):
    def __init__(self):
        super().__init__()
        self.condition = Condition.CS

class OpCodeBne(OpCodeBranch):
    def __init__(self):
        super().__init__()
        self.condition = Condition.NE

class OpCodeBeq(OpCodeBranch):
    def __init__(self):
        super().__init__()
        self.condition = Condition.EQ

class OpCodeBvc(OpCodeBranch):
    def __init__(self):
        super().__init__()
        self.condition = Condition.VC

class OpCodeBvs(OpCodeBranch):
    def __init__(self):
        super().__init__()
        self.condition = Condition.VS

class OpCodeBpl(OpCodeBranch):
    def __init__(self):
        super().__init__()
        self.condition = Condition.PL

class OpCodeBmi(OpCodeBranch):
    def __init__(self):
        super().__init__()
        self.condition = Condition.MI

class OpCodeBlt(OpCodeBranch):
    def __init__(self):
        super().__init__()
        self.condition = Condition.LT

class OpCodeBgt(OpCodeBranch):
    def __init__(self):
        super().__init__()
        self.condition = Condition.GT

class OpCodeBge(OpCodeBranch):
    def __init__(self):
        super().__init__()
        self.condition = Condition.GE

class OpCodeBle(OpCodeBranch):
    def __init__(self):
        super().__init__()
        self.condition = Condition.LE
