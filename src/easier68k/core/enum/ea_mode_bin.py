"""
EA Mode Binary Enum
Represents binary translations for various EA modes
"""
from .ea_mode import EAMode


class EAModeBinary:
    # Data register direct
    M_DRD = 0b000

    # Address register direct
    M_ARD = 0b001

    # Address register indirect
    M_ARI = 0b010

    # Address register indirect + post increment
    M_ARIPI = 0b011

    # Address register indirect + pre decrement
    M_ARIPD = 0b100

    # Immediate
    M_IMM = 0b111
    XN_IMM = 0b100

    # Absolute long address
    M_ALA = 0b111
    XN_ALA = 0b001

    # Absolute word address
    M_AWA = 0b111
    XN_AWA = 0b000

    @staticmethod
    def parse_from_ea_mode_mfirst(mode: EAMode) -> str:
        """
        Parses binary EA mode text from an EAMode class, returning the mode data first.
        :param mode: The EAMode to produce binary from
        :return: The parsed binary
        """
        if mode.mode == EAMode.DRD:
            return "{0:03b}{1:03b}".format(EAModeBinary.M_DRD, mode.data)
        if mode.mode == EAMode.ARD:
            return "{0:03b}{1:03b}".format(EAModeBinary.M_ARD, mode.data)
        if mode.mode == EAMode.ARI:
            return "{0:03b}{1:03b}".format(EAModeBinary.M_ARI, mode.data)
        if mode.mode == EAMode.ARIPI:
            return "{0:03b}{1:03b}".format(EAModeBinary.M_ARIPI, mode.data)
        if mode.mode == EAMode.ARIPD:
            return "{0:03b}{1:03b}".format(EAModeBinary.M_ARIPD, mode.data)
        if mode.mode == EAMode.IMM:
            return "{0:03b}100".format(EAModeBinary.M_IMM)
        if mode.mode == EAMode.ALA:
            return "{0:03b}001".format(EAModeBinary.M_ALA)
        if mode.mode == EAMode.AWA:
            return "{0:03b}000".format(EAModeBinary.M_AWA)

    @staticmethod
    def parse_from_ea_mode_xnfirst(mode: EAMode) -> str:
        """
        Parses binary EA mode text from an EAMode class, returning the Xn data first.
        :param mode: The EAMode to produce binary from
        :return: The parsed binary
        """
        if mode.mode == EAMode.DRD:
            return "{0:03b}{1:03b}".format(mode.data, EAModeBinary.M_DRD)
        if mode.mode == EAMode.ARD:
            return "{0:03b}{1:03b}".format(mode.data, EAModeBinary.M_ARD)
        if mode.mode == EAMode.ARI:
            return "{0:03b}{1:03b}".format(mode.data, EAModeBinary.M_ARI)
        if mode.mode == EAMode.ARIPI:
            return "{0:03b}{1:03b}".format(mode.data, EAModeBinary.M_ARIPI)
        if mode.mode == EAMode.ARIPD:
            return "{0:03b}{1:03b}".format(mode.data, EAModeBinary.M_ARIPD)
        if mode.mode == EAMode.IMM:
            return "100{0:03b}".format(EAModeBinary.M_IMM)
        if mode.mode == EAMode.ALA:
            return "001{0:03b}".format(EAModeBinary.M_ALA)
        if mode.mode == EAMode.AWA:
            return "000{0:03b}".format(EAModeBinary.M_AWA)
