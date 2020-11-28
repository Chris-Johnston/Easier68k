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
from .op_cmp import OpCodeCmp
from .op_branch import OpCodeBhi, OpCodeBls, OpCodeBcc, OpCodeBcs, OpCodeBne, OpCodeBeq, OpCodeBvc, OpCodeBvs, OpCodeBpl, OpCodeBmi, OpCodeBge, OpCodeBgt, OpCodeBle, OpCodeBra
from .op_trap import OpCodeTrap
from .op_lea import OpCodeLea
from .op_arithmetic_shift import OpCodeAsr, OpCodeAsl
from .op_simhalt import OpCodeSimHalt

# add more types by adding to this dict
OPCODE_LOOKUP = {
    "add": OpCodeAdd,
    "or": OpCodeOr,
    "sub": OpCodeSub,
    "and": OpCodeAnd,
    "move": OpCodeMove,
    "movea": OpCodeMove,
    "cmp": OpCodeCmp,
    "bhi": OpCodeBhi,
    "bls": OpCodeBls,
    "bcc": OpCodeBcc,
    "bcs": OpCodeBcs,
    "bne": OpCodeBne,
    "beq": OpCodeBeq,
    "bvc": OpCodeBvc,
    "bvs": OpCodeBvs,
    "bpl": OpCodeBpl,
    "bmi": OpCodeBmi,
    "bge": OpCodeBge,
    "bgt": OpCodeBgt,
    "ble": OpCodeBle,
    "trap": OpCodeTrap,
    "lea": OpCodeLea,
    "asl": OpCodeAsl,
    "asr": OpCodeAsr,
    "bt": OpCodeBra, # equivalent, will be interpreted as BT
    "bra": OpCodeBra,
    "simhalt": OpCodeSimHalt,
    "halt": OpCodeSimHalt,
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
