"""
EA Mode Binary Enum
Represents binary translations for various EA modes
"""
from .ea_mode import EAMode
from ..models.assembly_parameter import AssemblyParameter
from enum import IntEnum
from .op_size import OpSize


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

def get_mode_and_register_values(mode: EAMode) -> (int, int):
    """
    Gets the integer value representing the mode and register values for a given EAMode
    for use in the assembly process
    :param mode: EAMode to produce binary from
    :return:(the integer value of the assembled mode bits, the integer value of the assembled register bits)
    """
    return_mode = 0
    return_register = 0

    # get the return value for the register
    if mode.mode in [EAMode.DRD, EAMode.ARD, EAMode.ARI, EAMode.ARIPI, EAMode.ARIPD, EAMode.ARIPD]:
        return_register = mode.data
    elif mode.mode == EAMode.IMM:
        return_register = 0b100
    elif mode.mode == EAMode.ALA:
        return_register = 0b001
    elif mode.mode == EAMode.ALA:
        return_register = 0b000

    # get the return value for the mode by converting EAMode into EAModeBinary
    # this should instead a util method of EAMode
    if mode.mode == EAMode.DRD:
        return_mode = EAModeBinary.MODE_DRD
    if mode.mode == EAMode.ARD:
        return_mode = EAModeBinary.MODE_ARD
    if mode.mode == EAMode.ARI:
        return_mode = EAModeBinary.MODE_ARI
    if mode.mode == EAMode.ARIPI:
        return_mode = EAModeBinary.MODE_ARIPI
    if mode.mode == EAMode.ARIPD:
        return_mode = EAModeBinary.MODE_ARIPD
    if mode.mode == EAMode.IMM:
        return_mode = EAModeBinary.MODE_IMM
    if mode.mode == EAMode.ALA:
        return_mode = EAModeBinary.MODE_ALA
    if mode.mode == EAMode.AWA:
        return_mode = EAModeBinary.MODE_AWA

    # return both
    return return_mode, return_register


def parse_from_ea_mode_modefirst(mode: EAMode) -> int:
    """
    Parses binary EA mode text from an EAMode class, returning the mode data first.
    :param mode: The EAMode to produce binary from
    :return: The parsed binary
    """

    mode, reg = get_mode_and_register_values(mode)
    return mode << 3 | reg

def parse_from_ea_mode_regfirst(mode: EAMode) -> int:
    """
    Parses binary EA mode text from an EAMode class, returning the Xn data first.
    :param mode: The EAMode to produce binary from
    :return: The parsed binary
    """
    mode, reg = get_mode_and_register_values(mode)
    return reg << 3 | mode


def parse_ea_from_binary(mode: int, register: int, size: OpSize, is_source: bool, data : bytearray) -> (EAMode, int):
    """
    Takes in the paramaters and returns a newly constructed EAMode and the amount of
    words of data that it used. If the paramaters were illegal in any way then
    (None, 0) is returned

    Test that it handles source and destination behaviors properly
    >>> parse_ea_from_binary(EAModeBinary.MODE_IMM, EAModeBinary.REGISTER_IMM, OpSize.BYTE, False, bytearray.fromhex('A0'))
    (None, 0)
    
    >>> m = parse_ea_from_binary(EAModeBinary.MODE_IMM, EAModeBinary.REGISTER_IMM, OpSize.BYTE, True, bytearray.fromhex('A0'))

    >>> str(m[0])
    'EA Mode: EAMode.IMM, Data: 160'
    >>> m[1]
    1

    
    >>> m = parse_ea_from_binary(EAModeBinary.MODE_DRD, 0b010, OpSize.WORD, True, bytearray())

    >>> str(m[0])
    'EA Mode: EAMode.DRD, Data: 2'
    >>> m[1]
    0

    
    >>> m = parse_ea_from_binary(EAModeBinary.MODE_ARI, 0b110, OpSize.LONG, True, bytearray())

    >>> str(m[0])
    'EA Mode: EAMode.ARI, Data: 6'
    >>> m[1]
    0

    
    >>> m = parse_ea_from_binary(EAModeBinary.MODE_ALA, EAModeBinary.REGISTER_ALA, OpSize.LONG, False, bytearray.fromhex('00011000'))

    >>> str(m[0])
    'EA Mode: EAMode.ALA, Data: 69632'
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
            if size in [OpSize.WORD, OpSize.BYTE]:
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

    # map the ea mode integer to the enum
    if ea_mode == 0:
        ea_mode = EAMode.DRD
    elif ea_mode == 1:
        ea_mode = EAMode.ARD
    elif ea_mode == 2:
        ea_mode = EAMode.ARI
    elif ea_mode == 3:
        ea_mode = EAMode.ARIPI
    elif ea_mode == 4:
        ea_mode = EAMode.ARIPD
    elif ea_mode == 5:
        ea_mode = EAMode.IMM
    elif ea_mode == 6:
        ea_mode = EAMode.ALA
    elif ea_mode == 7:
        ea_mode = EAMode.AWA


    return (AssemblyParameter(ea_mode, ea_data), bytesUsed//2)
