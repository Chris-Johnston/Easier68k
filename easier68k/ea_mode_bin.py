"""
EA Mode Binary Enum
Represents binary translations for various EA modes
"""
from .ea_mode import EAMode
from .assembly_parameter import AssemblyParameter
from enum import IntEnum
from .op_size import OpSize

# delet this
class EAModeBinary(IntEnum):
    # Data register direct
    MODE_DRD = 0b000

    # Address register direct
    MODE_ARD = 0b001

    # Address register indirect
    MODE_ARI = 0b010

    # Address register indirect + post increment
    MODE_ARIPI = 0b011

    # Address register indirect + pre decrement
    MODE_ARIPD = 0b100

    # Immediate
    MODE_IMM = 0b111
    # REGISTER_IMM = 0b100

    # Absolute long address
    MODE_ALA = 0b111
    # REGISTER_ALA = 0b001

    # Absolute word address
    MODE_AWA = 0b111
    # REGISTER_AWA = 0b000
