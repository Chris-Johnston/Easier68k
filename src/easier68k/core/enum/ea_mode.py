"""
Represents an effective addressing mode
and methods associated with it
"""
from ..util.parsing import parse_literal


class EAMode:
    # Enum Values
    # Error value
    ERR = -1

    # Data register direct
    DRD = 0

    # Address register direct
    ARD = 1

    # Address register indirect
    ARI = 2

    # Address register indirect + post increment
    ARIPI = 3

    # Address register indirect + pre decrement
    ARIPD = 4

    # Immediate
    IMM = 5

    # Absolute long address
    ALA = 6

    # Absolute word address
    AWA = 7

    # Instance Values
    # Which mode this represents
    mode = ERR

    # Data value (could be register number, immediate data, or absolute address
    data = -1

    def __init__(self, mode=ERR, data=-1):
        self.mode = mode
        self.data = data

    def __str__(self):
        return "Mode: {}, Data: {}".format(self.mode, self.data)

    @staticmethod
    def parse_ea(addr: str):
        """
        Parses an effective addressing mode (such as D0, (A1), #$01)

        >>> EAMode.parse_ea('D')
        Traceback (most recent call last):
        ...
        AssertionError

        >>> str(EAMode.parse_ea('D3'))
        'Mode: 0, Data: 3'

        >>> str(EAMode.parse_ea('A6'))
        'Mode: 1, Data: 6'

        >>> str(EAMode.parse_ea('(A4)'))
        'Mode: 2, Data: 4'

        >>> str(EAMode.parse_ea('(A2)+'))
        'Mode: 3, Data: 2'

        >>> str(EAMode.parse_ea('(A2)-'))  # Invalid, can't do "post-decrement"
        Traceback (most recent call last):
        ...
        AssertionError

        >>> str(EAMode.parse_ea('($45).W'))
        "Mode: 7, Data: bytearray(b'E')"

        >>> str(EAMode.parse_ea('(%01010111).L'))
        "Mode: 6, Data: bytearray(b'W')"

        >>> str(EAMode.parse_ea('#$FF'))
        "Mode: 5, Data: bytearray(b'\\\\xff')"

        >>> str(EAMode.parse_ea('-(A2)'))
        'Mode: 4, Data: 2'
        """
        assert len(addr) >= 2

        if addr[0] == 'D':
            assert len(addr) == 2
            assert 0 <= int(addr[1]) <= 7
            return EAMode(EAMode.DRD, int(addr[1]))
        if addr[0] == 'A':
            assert len(addr) == 2
            assert 0 <= int(addr[1]) <= 7
            return EAMode(EAMode.ARD, int(addr[1]))
        if addr[0] == '(':  # ARI, ARIPI, ALA, or AWA
            # Parse the inside of the parentheses
            nested = ""
            found_paren = False

            i = 1
            while i < len(addr):
                if addr[i] == ')':
                    found_paren = True
                    break

                nested += addr[i]
                i += 1

            assert found_paren

            if addr[1] == 'A':  # ARI or ARIPI
                assert nested[0] == 'A'
                assert nested[1].isnumeric()
                assert 0 <= int(nested[1]) <= 7

                if i == len(addr) - 1:
                    return EAMode(EAMode.ARI, int(nested[1]))

                assert addr[i + 1] == '+'
                return EAMode(EAMode.ARIPI, int(nested[1]))

            # ALA or AWA
            assert i == len(addr) - 3
            assert addr[len(addr) - 1] == 'W' or addr[len(addr) - 1] == 'L'

            return EAMode(EAMode.AWA if addr[len(addr) - 1] == 'W' else EAMode.ALA, parse_literal(nested))
        if addr[0] == '#':  # IMM
            return EAMode(EAMode.IMM, parse_literal(addr[1:]))
        if addr[0] == '-':  # ARIPD
            assert len(addr) == 5
            assert addr[1] == '('
            assert addr[2] == 'A'
            assert addr[3].isnumeric()
            assert 0 <= int(addr[3]) <= 7
            assert addr[4] == ')'

            return EAMode(EAMode.ARIPD, int(addr[3]))

        return EAMode()

