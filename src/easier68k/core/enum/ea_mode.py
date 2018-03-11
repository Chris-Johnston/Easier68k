"""
Represents an effective addressing mode
and methods associated with it
"""
from ..util.parsing import parse_literal
from ...simulator.m68k import M68K
from ..enum.register import Register
from ..util.conversions import to_word


# should try to make this a constant only defined once
MAX_MEMORY_LOCATION = 16777216  # 2^24

class EAMode:
    # Enum Values
    # Error value
    ERR = -1
    Error = ERR

    # Data register direct
    DRD = 0
    DataRegisterDirect = DRD

    # Address register direct
    ARD = 1
    AddressRegisterDirect = ARD

    # Address register indirect
    ARI = 2
    AddressRegisterIndirect = ARI

    # Address register indirect + post increment
    ARIPI = 3
    AddressRegisterIndirectPostIncrement = ARIPI

    # Address register indirect + pre decrement
    ARIPD = 4
    AddressRegisterIndirectPreDecrement = ARIPD

    # Immediate
    IMM = 5
    Immediate = IMM

    # Absolute long address
    ALA = 6
    AbsoluteLongAddress = ALA

    # Absolute word address
    AWA = 7
    AbsoluteWordAddress = AWA

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

    def get_value(self, simulator: M68K) -> int:
        """
        Gets the value for this EAMode
        :param simulator:
        :return:
        """
        if self.mode is EAMode.IMM:
            return self.data

        if self.mode is EAMode.DRD:
            # convert the data into the register value
            assert 0 <= self.data <= 7
            data_register = Register(self.data)
            return simulator.get_register_value(data_register)

        if self.mode is EAMode.AddressRegisterDirect:
            # address register direct gets the value of the register
            assert Register.A0 <= self.data <= Register.A7
            # offset the value to compensate for the enum offset
            addr_register = Register(self.data - Register.A0)
            # get the value of the register, that's it
            return simulator.get_register_value(addr_register)

        if self.mode is EAMode.AddressRegisterIndirect:
            # address register indirect gets the value that the register points to
            # check that the register number is valid
            assert Register.A0 <= self.data <= Register.A7
            # offset the value to compensate for the enum offset
            addr_register = Register(self.data - Register.A0)
            # this gets the value of the register, which points to a location
            # in memory where the target value is
            register_value = simulator.get_register_value(addr_register)
            # now get the value in memory of that register
            return simulator.memory.get(2, register_value)

        if self.mode is EAMode.AddressRegisterIndirectPostIncrement:
            # address register indirect gets the value that the register points to
            # check that the register number is valid
            assert Register.A0 <= self.data <= Register.A7
            # offset the value to compensate for the enum offset
            addr_register = Register(self.data - Register.A0)
            # this gets the value of the register, which points to a location
            # in memory where the target value is
            register_value = simulator.get_register_value(addr_register)
            # now get the value in memory of that register
            val = simulator.memory.get(2, register_value)
            # do the post increment
            simulator.set_register_value(addr_register, register_value + 1)
            # return the value
            return val

        if self.mode is EAMode.AddressRegisterIndirectPreDecrement:
            # address register indirect gets the value that the register points to
            # check that the register number is valid
            assert Register.A0 <= self.data <= Register.A7
            # offset the value to compensate for the enum offset
            addr_register = Register(self.data - Register.A0)
            # this gets the value of the register, which points to a location
            # in memory where the target value is
            register_value = simulator.get_register_value(addr_register)

            # do the pre decrement (this does not update the value of register_value)
            simulator.set_register_value(addr_register, register_value - 1)

            # now get the value in memory of that register
            # and return that value
            return simulator.memory.get(2, register_value - 1)

        if self.mode in [EAMode.AbsoluteLongAddress, EAMode.AbsoluteWordAddress]:
            # if mode is absolute long or word address
            # then get the value in memory for that value

            # ensure that the data is valid
            assert 0 <= self.data <= MAX_MEMORY_LOCATION, 'The address must be in the range [0, 2^24]!'

            # get the address being looked for
            addr = self.data

            # if word address, mask out extra bits
            if self.mode is EAMode.AbsoluteWordAddress:
                addr = to_word(addr)

            # now get the value at that memory location
            return simulator.memory.get(4, addr)

        # if nothing was done by now, surely something must be wrong
        assert False, 'Invalid effective addressing mode!'

    def set_value(self, simulator: M68K, value: int):
        """
        Sets the value for the
        :param simulator:
        :param value:
        :return:
        """

        if self.mode is EAMode.DRD:
            # set the value for the data register
            assert 0 <= self.data <= 7
            data_register = Register(self.data)
            simulator.set_register_value(data_register, value)

        if self.mode is EAMode.ARD:
            # set the value for the address register
            assert 0 <= self.data <= 7
            addr_register = Register(self.data - Register.A0)
            simulator.set_register_value(addr_register, value)
        #todo implement the other modes

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

