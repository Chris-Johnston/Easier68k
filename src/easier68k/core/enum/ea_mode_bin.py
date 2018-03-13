"""
EA Mode Binary Enum
Represents binary translations for various EA modes
"""
from .ea_mode import EAMode
from ..models.assembly_parameter import AssemblyParameter
from enum import IntEnum


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
    REGISTER_IMM = 0b100

    # Absolute long address
    MODE_ALA = 0b111
    REGISTER_ALA = 0b001

    # Absolute word address
    MODE_AWA = 0b111
    REGISTER_AWA = 0b000

# currently missing the offset modes
VALID_DEST_EA_MODES = [EAModeBinary.MODE_DRD, EAModeBinary.MODE_ARI,
                       EAModeBinary.MODE_ARIPI, EAModeBinary.MODE_ARIPD,
                       EAModeBinary.MODE_ALA, EAModeBinary.MODE_AWA]

# currently missing the offset modes
VALID_SRC_EA_MODES = VALID_DEST_EA_MODES + [EAModeBinary.MODE_ARD, EAModeBinary.MODE_IMM]

# what the hell should I name this?
# it's the valid destination registers for the 111 mode
# currently missing the offset modes
VALID_DEST_EA_111_REGISTERS = [EAModeBinary.REGISTER_ALA, EAModeBinary.REGISTER_AWA]

# what the hell should I name this?
# it's the valid source registers for the 111 mode
# currently missing the offset modes
VALID_SRC_EA_111_REGISTERS = VALID_DEST_EA_111_REGISTERS + [EAModeBinary.REGISTER_IMM]


def parse_from_ea_mode_modefirst(mode: EAMode) -> str:
    """
    Parses binary EA mode text from an EAMode class, returning the mode data first.
    :param mode: The EAMode to produce binary from
    :return: The parsed binary
    """
    if mode.mode == EAMode.DRD:
        return "{0:03b}{1:03b}".format(EAModeBinary.MODE_DRD, mode.data)
    if mode.mode == EAMode.ARD:
        return "{0:03b}{1:03b}".format(EAModeBinary.MODE_ARD, mode.data)
    if mode.mode == EAMode.ARI:
        return "{0:03b}{1:03b}".format(EAModeBinary.MODE_ARI, mode.data)
    if mode.mode == EAMode.ARIPI:
        return "{0:03b}{1:03b}".format(EAModeBinary.MODE_ARIPI, mode.data)
    if mode.mode == EAMode.ARIPD:
        return "{0:03b}{1:03b}".format(EAModeBinary.MODE_ARIPD, mode.data)
    if mode.mode == EAMode.IMM:
        return "{0:03b}100".format(EAModeBinary.MODE_IMM)
    if mode.mode == EAMode.ALA:
        return "{0:03b}001".format(EAModeBinary.MODE_ALA)
    if mode.mode == EAMode.AWA:
        return "{0:03b}000".format(EAModeBinary.MODE_AWA)


def parse_from_ea_mode_regfirst(mode: EAMode) -> str:
    """
    Parses binary EA mode text from an EAMode class, returning the Xn data first.
    :param mode: The EAMode to produce binary from
    :return: The parsed binary
    """
    if mode.mode == EAMode.DRD:
        return "{0:03b}{1:03b}".format(mode.data, EAModeBinary.MODE_DRD)
    if mode.mode == EAMode.ARD:
        return "{0:03b}{1:03b}".format(mode.data, EAModeBinary.MODE_ARD)
    if mode.mode == EAMode.ARI:
        return "{0:03b}{1:03b}".format(mode.data, EAModeBinary.MODE_ARI)
    if mode.mode == EAMode.ARIPI:
        return "{0:03b}{1:03b}".format(mode.data, EAModeBinary.MODE_ARIPI)
    if mode.mode == EAMode.ARIPD:
        return "{0:03b}{1:03b}".format(mode.data, EAModeBinary.MODE_ARIPD)
    if mode.mode == EAMode.IMM:
        return "100{0:03b}".format(EAModeBinary.MODE_IMM)
    if mode.mode == EAMode.ALA:
        return "001{0:03b}".format(EAModeBinary.MODE_ALA)
    if mode.mode == EAMode.AWA:
        return "000{0:03b}".format(EAModeBinary.MODE_AWA)
    


def parse_ea_from_binary(mode: int, register: int, size: chr, is_source: bool, data : bytearray) -> (EAMode, int):
    """
    Takes in the paramaters and returns a newly constructed EAMode and the amount of
    words of data that it used. If the paramaters were illegal in any way then
    (None, 0) is returned
    
    Test that it handles source and destination behaviors properly
    >>> parse_ea_from_binary(EAModeBinary.MODE_IMM, EAModeBinary.REGISTER_IMM, 'B', False, bytearray.fromhex('A0'))
    (None, 0)
    
    >>> m = parse_ea_from_binary(EAModeBinary.MODE_IMM, EAModeBinary.REGISTER_IMM, 'B', True, bytearray.fromhex('A0'))
    >>> str(m[0])
    'EA Mode: 5, Data: 160'
    >>> m[1]
    1
    
    >>> m = parse_ea_from_binary(EAModeBinary.MODE_DRD, 0b010, 'W', True, bytearray())
    >>> str(m[0])
    'EA Mode: 0, Data: 2'
    >>> m[1]
    0
    
    >>> m = parse_ea_from_binary(EAModeBinary.MODE_ARI, 0b110, 'L', True, bytearray())
    >>> str(m[0])
    'EA Mode: 2, Data: 6'
    >>> m[1]
    0
    
    >>> m = parse_ea_from_binary(EAModeBinary.MODE_ALA, EAModeBinary.REGISTER_ALA, 'L', False, bytearray.fromhex('00011000'))
    >>> str(m[0])
    'EA Mode: 6, Data: 69632'
    >>> m[1]
    2
    
    :param mode: the binary mode bits retrieved from the instruction 
    :param register: the binary register bits retrieved from the instruction
    :param size: the alphabetical size (i.e. one of 'BLW')
    :param is_source: is this the source or destination ea? 
    :param data: extra data that follows after the command that might be needed
    :return: an EAMode constructed from the given parameters and how many words were used from data
    """
    bytesUsed = 0
    
    # check source mode
    if is_source and not mode in VALID_SRC_EA_MODES:
        return (None, 0)
    
    if not is_source and not mode in VALID_DEST_EA_MODES:
        return (None, 0)
    
    ea_data = register
    
    # these only differ when mode is 0b111
    ea_mode = mode
    
    
    # check source register
    if mode == 0b111:
        if is_source and not register in VALID_SRC_EA_111_REGISTERS:
            return (None, 0)
        
        if not is_source and not register in VALID_DEST_EA_111_REGISTERS:
            return (None, 0)
        
        # handle the three special cases for when mode is 7
        if register == EAModeBinary.REGISTER_AWA:
            ea_data =  int.from_bytes(data[bytesUsed:bytesUsed+2], 'big')
            bytesUsed += 2
            ea_mode = 7
            
        elif register == EAModeBinary.REGISTER_ALA:
            ea_data =  int.from_bytes(data[bytesUsed:bytesUsed+4], 'big')
            bytesUsed += 4
            ea_mode = 6
            
        elif is_source and register == EAModeBinary.REGISTER_IMM:
            if size in 'BW':
                # TODO: Do we check for bytes that the left byte is all
                # zeros, or do we do this where we assume the assembler is right
                ea_data =  int.from_bytes(data[bytesUsed:bytesUsed+2], 'big')
                bytesUsed += 2
            else: #must be L
                ea_data =  int.from_bytes(data[bytesUsed:bytesUsed+4], 'big')
                bytesUsed += 4
            ea_mode = 5
        
        else:
            return (None, 0)
    
    return (AssemblyParameter(ea_mode, ea_data), bytesUsed//2)
