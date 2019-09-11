"""
Assembly Parameter

Represents a single parameter in assembly code
this is the new 'EAMode' class
"""

from .ea_mode import EAMode
from .register import Register, ALL_ADDRESS_REGISTERS
from .m68k import M68K
from .conversions import to_word
from .memory_value import MemoryValue
from .op_size import OpSize

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

    def get_value(self, simulator: M68K, length: OpSize = OpSize.WORD) -> MemoryValue:
        """
        Gets the value for this EAMode from the simulator
        :param simulator: reference to the 68k simulator
        :param length: the length in bytes associated with this operation, must be 1 2 or 4
        :return: the value associated with this assembly parameter
        """
        # this check is probably useless now that the enum is being used
        assert length in [OpSize.BYTE, OpSize.WORD, OpSize.LONG], 'The length for this operation must be 1 2 or 4 bytes!'

        # immediates are assumed to be signed values
        if self.mode is EAMode.IMM:
            ret = MemoryValue(OpSize(length))
            if self.data < 0:
                ret.set_value_signed_int(self.data)
            else:
                ret.set_value_unsigned_int(self.data)
            return ret

        if self.mode is EAMode.DRD:
            # convert the data into the register value
            assert 0 <= self.data <= 7
            data_register = Register(self.data)
            return simulator.get_register(data_register)

        if self.mode is EAMode.AddressRegisterDirect:
            # address register direct gets the value of the register
            assert Register.A0 <= self.data + Register.A0 <= Register.A7
            # offset the value to compensate for the enum offset
            addr_register = Register(self.data + Register.A0)
            # get the value of the register, that's it
            return simulator.get_register(addr_register)

        if self.mode is EAMode.AddressRegisterIndirect:
            # address register indirect gets the value that the register points to
            # check that the register number is valid
            assert Register.A0.value <= self.data + Register.A0.value <= Register.A7.value
            # offset the value to compensate for the enum offset
            addr_register = Register(self.data + Register.A0.value)
            # this gets the value of the register, which points to a location
            # in memory where the target value is
            register_value = simulator.get_register(addr_register)
            # now get the value in memory of that register
            val = simulator.memory.get(length, register_value.get_value_unsigned())
            return val

        if self.mode is EAMode.AddressRegisterIndirectPostIncrement:
            # address register indirect gets the value that the register points to
            # check that the register number is valid
            assert Register.A0.value <= self.data + Register.A0.value <= Register.A7.value
            # offset the value to compensate for the enum offset
            addr_register = Register(self.data + Register.A0.value)
            # this gets the value of the register, which points to a location
            # in memory where the target value is
            register_value = simulator.get_register(addr_register)
            # now get the value in memory of that register
            val = simulator.memory.get(OpSize.LONG, register_value.get_value_unsigned())
            total = register_value.get_value_unsigned() + OpSize.LONG.value
            mv = MemoryValue(OpSize.LONG, unsigned_int=total)

            # do the post increment
            simulator.set_register(addr_register, mv)

            return val

        if self.mode is EAMode.AddressRegisterIndirectPreDecrement:
            # address register indirect gets the value that the register points to
            # check that the register number is valid
            assert Register.A0 <= self.data + Register.A0 <= Register.A7
            # offset the value to compensate for the enum offset
            addr_register = Register(self.data + Register.A0)
            # this gets the value of the register, which points to a location
            # in memory where the target value is
            register_value = simulator.get_register(addr_register)

            total = register_value.get_value_unsigned() - OpSize.LONG.value
            mv = MemoryValue(OpSize.LONG, unsigned_int=total)

            # do the pre decrement (this does not update the value of register_value)
            simulator.set_register(addr_register, mv)

            # now get the value in memory of that register
            # and return that value
            return simulator.memory.get(OpSize.LONG, register_value.get_value_unsigned())

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
            return MemoryValue(OpSize.LONG, unsigned_int=addr)

        # if nothing was done by now, surely something must be wrong
        assert False, 'Invalid effective addressing mode!'

    def set_value(self, simulator: M68K, value: MemoryValue):
        """
        Sets the value of a destination mode
        :param simulator: the reference to the simulator
        :param value: the value to set for this assembly parameter
        :param length: the number of bits associated for this instruction, must be 1 2 or 4
        :return:
        """
        if not isinstance(value, MemoryValue):
            raise AssertionError("The value parameter must be of type MemoryValue")

        if self.mode is EAMode.Immediate:
            assert False, 'Cannot set the value of an immediate.'

        if self.mode is EAMode.DRD:
            # set the value for the data register
            assert 0 <= self.data <= 7
            data_register = Register(self.data)
            simulator.set_register(data_register, value)

        if self.mode is EAMode.AddressRegisterDirect:
            # set the value for the address register
            # only ensure that it is referring to a valid address register
            # since this is a direct addressing mode, and not treated as a 'pointer'
            # to memory, this is not bounded by the number of address lines
            assert 0 <= self.data <= 7
            addr_register = Register(self.data + Register.A0)
            simulator.set_register(addr_register, value)

        if self.mode is EAMode.AddressRegisterIndirect:
            # sets the value in memory that the address register points to
            assert 0 <= self.data <= 7
            assert 0 <= value.get_value_unsigned() <= MAX_MEMORY_LOCATION, 'The value must fit in the memory space [0, 2^24]'
            addr_register = Register(self.data + Register.A0)
            location = simulator.get_register(addr_register).get_value_unsigned()
            simulator.memory.set(value.length, location, value)

        if self.mode is EAMode.AddressRegisterIndirectPreDecrement:
            # sets the value in memory that the address register points to
            assert 0 <= self.data <= 7
            assert 0 <= value.get_value_unsigned() <= MAX_MEMORY_LOCATION, 'The value must fit in the memory space [0, 2^24]'
            addr_register = Register(self.data + Register.A0)
            location = simulator.get_register(addr_register).get_value_unsigned()
            location -= value.length.get_number_of_bytes()
            simulator.set_register(addr_register, MemoryValue(OpSize.LONG, unsigned_int=location))
            simulator.memory.set(value.length, location, value)

        if self.mode is EAMode.AddressRegisterIndirectPostIncrement:
            # sets the value in memory that the address register points to
            assert 0 <= self.data <= 7
            assert 0 <= value.get_value_unsigned() <= MAX_MEMORY_LOCATION, 'The value must fit in the memory space [0, 2^24]'

            addr_register = Register(self.data + Register.A0)
            location = simulator.get_register(addr_register).get_value_unsigned()
            simulator.memory.set(value.length, location, value)
            location += value.length.get_number_of_bytes()
            simulator.set_register(addr_register, MemoryValue(OpSize.LONG, unsigned_int=location))


        if self.mode in [EAMode.AbsoluteLongAddress, EAMode.AbsoluteWordAddress]:
            # assert that the value fits in the bounds of memory
            assert 0 <= self.data <= MAX_MEMORY_LOCATION
            assert 0 <= value.get_value_unsigned() <= 0xFFFFFFFF, 'The value must fit inside of a long word!'

            # if the mode is a word
            if self.mode is EAMode.AbsoluteWordAddress:
                # mask it to only be a word
                value = MemoryValue(value.length, unsigned_int=to_word(value.get_value_unsigned()))

            # set the value in memory to that
            simulator.memory.set(value.length, self.data, value)
