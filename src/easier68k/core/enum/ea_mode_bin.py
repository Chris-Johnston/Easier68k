"""
EA Mode Binary Enum
Represents binary translations for various EA modes
"""
from .ea_mode import EAMode


class EAModeBinary:
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
    VALID_DEST_EA_MODES = [MODE_DRD, MODE_ARI, MODE_ARIPI, MODE_ARIPD, MODE_ALA, MODE_AWA]
    
    # currently missing the offset modes
    VALID_SRC_EA_MODES = VALID_DEST_EA_MODES + [MODE_ARD, MODE_IMM]
    
    # what the hell should I name this?
    # it's the valid destination registers for the 111 mode
    # currently missing the offset modes
    VALID_DEST_EA_111_REGISTERS = [REGISTER_ALA, REGISTER_AWA]
    
    # what the hell should I name this?
    # it's the valid source registers for the 111 mode
    # currently missing the offset modes
    VALID_SRC_EA_111_REGISTERS = VALID_DEST_EA_111_REGISTERS + [REGISTER_IMM]

    @staticmethod
    def parse_from_ea_mode_mfirst(mode: EAMode) -> str:
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

    @staticmethod
    def parse_from_ea_mode_xnfirst(mode: EAMode) -> str:
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
