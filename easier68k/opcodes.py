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
from .op_add import OpCodeAdd
from .op_or import OpCodeOr
from .op_and import OpCodeAnd
from .op_sub import OpCodeSub
from .op_move import OpCodeMove

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
