"""
Assembly Parameter

Represents a single parameter in assembly code
this is the new 'EAMode' class
"""

from ..enum.ea_mode import EAMode
from ..enum.register import Register
from ...simulator.m68k import M68K
from ..util.conversions import to_word

# should try to make this a constant only defined once
MAX_MEMORY_LOCATION = 16777216  # 2^24


class AssemblyParameter:

    def __init__(self, mode: EAMode, data: int):
        """
        Constructor

        Checks that the mode and the data are considered to be valid, like
        registers are within the correct bounds and addresses are not out of bounds.
        """
        # ensure that the values are valid

        # when referencing a register, ensure that the data is within [0, 7]
        if mode in [EAMode.DataRegisterDirect, EAMode.AddressRegisterIndirectPreDecrement,
                    EAMode.AddressRegisterIndirect, EAMode.AddressRegisterIndirectPostIncrement,
                    EAMode.AddressRegisterDirect]:
            assert 0 <= data <= 7, 'The register number for this mode must be in the range [0, 7]!'

        if mode in [EAMode.AbsoluteWordAddress, EAMode.AbsoluteLongAddress]:
            # ensure that the address isn't outside the bounds of max memory location
            # and is greater than or eq to 0
            assert 0 <= data <= MAX_MEMORY_LOCATION, 'An absolute address must be in the bounds [0, 2^24]!'

        if mode is EAMode.Immediate:
            # ensure that the value isn't too large, cannot be larger than a long word
            # negative values need to be converted into unsigned integers
            assert -2147483648 <= data <= 2147483647 or 0 <= data <= 0xFFFFFFFF, 'Value must fit inside a long word!'

        # set values
        self.mode = mode
        self.data = data

    def __str__(self):
        """
        str util method
        :return:
        """
        return "EA Mode: {}, Data: {}".format(self.mode, self.data)

    def get_value(self, simulator: M68K, length: int = 4) -> int:
        """
        Gets the value for this EAMode from the simulator
        :param simulator: reference to the 68k simulator
        :param length: the length in bytes associated with this operation, must be 1 2 or 4
        :return: the value associated with this assembly parameter
        """
        assert length in [1, 2, 4], 'The length for this operation must be 1 2 or 4 bytes!'

        if self.mode is EAMode.IMM:
            return self.data

        if self.mode is EAMode.DRD:
            # convert the data into the register value
            assert 0 <= self.data <= 7
            data_register = Register(self.data)
            return simulator.get_register_value(data_register)

        if self.mode is EAMode.AddressRegisterDirect:
            # address register direct gets the value of the register
            assert Register.A0 <= self.data + Register.A0 <= Register.A7
            # offset the value to compensate for the enum offset
            addr_register = Register(self.data + Register.A0)
            # get the value of the register, that's it
            return simulator.get_register_value(addr_register)

        if self.mode is EAMode.AddressRegisterIndirect:
            # address register indirect gets the value that the register points to
            # check that the register number is valid
            assert Register.A0 <= self.data + Register.A0 <= Register.A7
            # offset the value to compensate for the enum offset
            addr_register = Register(self.data + Register.A0)
            # this gets the value of the register, which points to a location
            # in memory where the target value is
            register_value = simulator.get_register_value(addr_register)
            # now get the value in memory of that register
            return int.from_bytes(simulator.memory.get(length, register_value), byteorder='big', signed=False)

        if self.mode is EAMode.AddressRegisterIndirectPostIncrement:
            # address register indirect gets the value that the register points to
            # check that the register number is valid
            assert Register.A0 <= self.data + Register.A0 <= Register.A7
            # offset the value to compensate for the enum offset
            addr_register = Register(self.data + Register.A0)
            # this gets the value of the register, which points to a location
            # in memory where the target value is
            register_value = simulator.get_register_value(addr_register)
            # now get the value in memory of that register
            val = simulator.memory.get(length, register_value)
            # do the post increment
            simulator.set_register_value(addr_register, register_value + length)
            # return the value
            return int.from_bytes(val, byteorder='big', signed=False)

        if self.mode is EAMode.AddressRegisterIndirectPreDecrement:
            # address register indirect gets the value that the register points to
            # check that the register number is valid
            assert Register.A0 <= self.data + Register.A0 <= Register.A7
            # offset the value to compensate for the enum offset
            addr_register = Register(self.data + Register.A0)
            # this gets the value of the register, which points to a location
            # in memory where the target value is
            register_value = simulator.get_register_value(addr_register)

            # do the pre decrement (this does not update the value of register_value)
            simulator.set_register_value(addr_register, register_value - length)

            # now get the value in memory of that register
            # and return that value
            return int.from_bytes(simulator.memory.get(length, register_value - length), byteorder='big', signed=False)

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

            # now get the value of that absolute long address
            return addr

        # if nothing was done by now, surely something must be wrong
        assert False, 'Invalid effective addressing mode!'

    def set_value(self, simulator: M68K, value: int, length: int = 4):
        """
        Sets the value of a destination mode
        :param simulator: the reference to the simulator
        :param value: the value to set for this assembly parameter
        :param length: the number of bits associated for this instruction, must be 1 2 or 4
        :return:
        """

        assert length in [1, 2, 4], 'The value of length must be 1 2 or 4!'

        if self.mode is EAMode.Immediate:
            assert False, 'Cannot set the value of an immediate.'

        if self.mode is EAMode.DRD:
            # set the value for the data register
            assert 0 <= self.data <= 7

            # if value is negative, then need to take 2s comp
            if value < 0:
                mask = 0xFF
                if length is 2:
                    mask = 0xFFFF
                if length is 4:
                    mask = 0xFFFFFFFF

                value = value ^ mask
                value += 1
                value = abs(value)

            assert 0 <= value <= 0xFFFFFFFF, 'The value must fit in a long word'
            data_register = Register(self.data)
            simulator.set_register_value(data_register, value)

        if self.mode is EAMode.AddressRegisterDirect:
            # set the value for the address register
            assert 0 <= self.data <= 7
            assert 0 <= value <= MAX_MEMORY_LOCATION, 'The value must fit in the memory space [0, 2^24]'
            addr_register = Register(self.data + Register.A0)
            simulator.set_register_value(addr_register, value)

        if self.mode is EAMode.AddressRegisterIndirect:
            # sets the value in memory that the address register points to
            assert 0 <= self.data <= 7
            assert 0 <= value <= MAX_MEMORY_LOCATION, 'The value must fit in the memory space [0, 2^24]'
            addr_register = Register(self.data + Register.A0)
            location = simulator.get_register_value(addr_register)
            simulator.memory.set(length, location, value.to_bytes(length, 'big'))

        if self.mode is EAMode.AddressRegisterIndirectPreDecrement:
            # sets the value in memory that the address register points to
            assert 0 <= self.data <= 7
            assert 0 <= value <= MAX_MEMORY_LOCATION, 'The value must fit in the memory space [0, 2^24]'
            addr_register = Register(self.data + Register.A0)
            location = simulator.get_register_value(addr_register)
            location -= length
            simulator.set_register_value(addr_register, location)
            simulator.memory.set(length, location, value.to_bytes(length, 'big'))

        if self.mode is EAMode.AddressRegisterIndirectPostIncrement:
            # sets the value in memory that the address register points to
            assert 0 <= self.data <= 7
            assert 0 <= value <= MAX_MEMORY_LOCATION, 'The value must fit in the memory space [0, 2^24]'

            addr_register = Register(self.data + Register.A0)
            location = simulator.get_register_value(addr_register)

            simulator.memory.set(length, location, value.to_bytes(length, 'big'))

            location += length
            simulator.set_register_value(addr_register, location)

        if self.mode in [EAMode.AbsoluteLongAddress, EAMode.AbsoluteWordAddress]:
            # assert that the value fits in the bounds of memory
            assert 0 <= self.data <= MAX_MEMORY_LOCATION
            assert 0 <= value <= 0xFFFFFFFF, 'The value must fit inside of a long word!'

            # if the mode is a word
            if self.mode is EAMode.AbsoluteWordAddress:
                # mask it to only be a word
                value = to_word(value)

            # set the value in memory to that
            simulator.memory.set(length, self.data, value.to_bytes(length, 'big'))
