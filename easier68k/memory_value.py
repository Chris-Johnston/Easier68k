"""
Memory Value

Representation of some value in memory with a length of a Byte, Word or Long Word,
which can either be an array of bytes, an integer number, a single character
or an array of characters.

Supports operations like adding, subtracting, shift left, shift right, bitwise OR AND XOR, equals

Supports getting the most significant bit, determining the signed or unsigned integer values, the value
as a array of bytes, the value as a hex string.

This was done to keep the interal handling of memory values consistent, instead of conversions back and forth between
integers, hex strings and byte arrays.
"""

from .op_size import OpSize


def mask_value_for_length(size: OpSize, unsigned_value: int) -> int:
    """
    Masks an unsigned value to a certain size
    :param size:
    :param unsigned_value:
    :return:
    """
    if size is OpSize.BYTE:
        return 0xFF & unsigned_value
    if size is OpSize.WORD:
        return 0xFFFF & unsigned_value
    if size is OpSize.LONG:
        return 0xFFFFFFFF & unsigned_value
    return None


class MemoryValue:
    """
    Representation of some value in memory
    """

    def __init__(self, len: OpSize = OpSize.WORD, *,
                 signed_int: int = None,
                 unsigned_int: int = None,
                 bytes: bytearray = None):
        """
        Constructor

        Sets the initial value to zero with a length of OpSize.Wordprint
        :param len the length in bytes of this memory value
        :param signed_int the value to set as a signed int
        :param unsigned_int the value to set as an unsigned int
        :param bytes the value to set as a bytearray
        """
        # use OpSize for length in bytes
        self.length = len

        if signed_int is not None:
            self.set_value_signed_int(signed_int)
        elif unsigned_int is not None:
            self.set_value_unsigned_int(unsigned_int)
        elif bytes is not None:
            self.set_value_bytes(bytes)
        else:
            # use integers as the interal storage of the value
            # this should be an UNSIGNED value
            self.unsigned_value = 0

        # consider adding CCR bits for the last operation?
        # or just have CCR bit getters, in the ops just compare before and after

    def set_size(self, size: OpSize):
        """
        Sets the length of this memory value
        :param size: the length in bytes of this value, defined by OpSize
        :return: None
        """
        self.length = size

    def get_size(self) -> OpSize:
        """
        Gets the length of this memory value as an OpSize
        :return: the length in bytes of this value as defined by an OpSize
        """
        return self.length

    def set_value_signed_int(self, signed_int: int):
        """
        Sets the value of this MemoryValue from a signed int
        :param signed_int:
        :return:
        """
        if not isinstance(signed_int, int):
            raise AssertionError('The signed_int parameter must be an integer!')

        # assert that the value can fit within the possible range for the size
        if self.length is OpSize.BYTE:
            assert (-128 <= signed_int <= 127), 'Value must fit in the range [-128, 127].'
        if self.length is OpSize.WORD:
            assert (-32768 <= signed_int <= 32767), 'Value must fit in the range [-32768, 32767]'
        if self.length is OpSize.LONG:
            assert (-2147483648 <= signed_int <= 2147483647), 'Value must fit in the range [-2147483648, 2147483647]'

        # if the value is negative, take the 2s comp for the length
        if signed_int < 0:
            self.unsigned_value = self.__twos_complement(abs(signed_int), self.length)
        else:
            self.unsigned_value = signed_int

    def set_value_unsigned_int(self, unsigned_int: int):
        """
        Sets the value of this MemoryValue from an unsigned int
        :param unsigned_int:
        :return:
        """
        if not isinstance(unsigned_int, int):
           raise AssertionError(f'The unsigned_int parameter must be an integer! Was {type(unsigned_int)}')

        # assert that the value can fit within the possible range for the size
        if self.length is OpSize.LONG:
            assert (0 <= unsigned_int <= 0xFFFFFFFF), 'Value must fit in the range [0, 0xFFFFFFFF].'
        if self.length is OpSize.WORD:
            assert (0 <= unsigned_int <= 0xFFFF), 'Value must fit in the range [0, 0xFFFF]'
        if self.length is OpSize.BYTE:
            assert (0 <= unsigned_int <= 0xFF), 'Value must fit in the range [0, 0xFF]'

        self.unsigned_value = unsigned_int

    def set_value_bytes(self, bytes_value: bytes):
        """
        Sets the value of this MemoryValue from an array of bytes
        :param bytes_value:
        :return:
        """
        if not (isinstance(bytes_value, bytes) or isinstance(bytes_value, bytearray)):
            raise AssertionError('The bytes_value parameter must be bytes or bytearray!')

        # optional, should we trim the input bytes to fit to the length of this
        # get the value from bytes
        val = int.from_bytes(bytes=bytes_value, byteorder='big', signed=False)
        # then set it using the set value unsigned method to perform checking
        self.set_value_unsigned_int(val)

    @staticmethod
    def __twos_complement(value: int, length: OpSize) -> int:
        """
        Returns the twos complement of the given value
        :pasram value: the value to take the 2s comp of
        :param length: the length in bytes of the value
        :return:
        """

        # flip all of the bits and set the value
        mask = 0xFF
        if length is OpSize.WORD:
            mask = 0xFFFF
        elif length is OpSize.LONG:
            mask = 0xFFFFFFFF

        return (value ^ mask) + 1

    def get_value_unsigned(self):
        """
        Gets the unsigned value
        :return:
        """
        return self.unsigned_value

    def get_value_signed(self):
        """
        Gets the signed value
        :return:
        """
        # if the msb is set
        if self.get_msb():
            ret_val = self.__twos_complement(self.unsigned_value, self.length)
            return -1 * ret_val
        # otherwise, is positive and don't have to convert
        return self.unsigned_value

    def get_negative(self):
        """
        Gets the negative flag for the memory value
        :return:
        """
        return self.get_msb()
    
    def get_zero(self):
        """
        Gets a value indicating if the value is equal to zero.
        """
        return self.get_value_unsigned() == 0

    def get_value_bytes(self) -> bytes:
        """
        Get the bytes value
        :return:
        """
        return self.__bytes__()

    def get_value_bytearray(self) -> bytearray:
        """
        Get the value as a bytearray
        :return:
        """
        return bytearray(self.__bytes__())

    def get_msb(self, size: OpSize=None) -> bool:
        """
        Get the most significant bit indicating that the value is negative
        :return: Returns the bool value of the MSB.
        """
        if size is None:
            size = self.length

        # default mask is one byte
        mask = 0x80
        if size is OpSize.WORD:
            mask = 0x8000
        elif size is OpSize.LONG:
            mask = 0x80000000

        # determine if the unsigned value MSB is set to 1
        # by masking only the MSB and checking that the result
        # has some value set
        return self.unsigned_value & mask > 0

    def __eq__(self, other) -> bool:
        """
        Equals, compares to see that the value is the same
        don't care about the len
        :param other:
        :return:
        """
        if isinstance(other, MemoryValue):
            return self.get_value_signed() == other.get_value_signed()
        elif isinstance(other, int):
            return self.get_value_signed() == other
        return NotImplemented

    def add_unsigned(self, other):
        total = self.get_value_unsigned() + other.get_value_unsigned()
        # 1/21 TODO
        # tfw your todo messages need to start including a year
        # set when the register cannot properly represent the result as a signed value (you overflowed into the sign bit). 
        carry = False
        if self.length == OpSize.BYTE:
            carry = total > 0xFF # this might be wrong?
        elif self.length == OpSize.WORD:
            carry = total > 0xFFFF
        elif self.length == OpSize.LONG:
            carry = total > 0xFFFF_FFFF
        overflow = False
        return MemoryValue(self.length, unsigned_int=total), carry, overflow

    def sub_unsigned(self, other):
        # TODO: need to sanity check the overflow condition
        total = self.get_value_unsigned() - other.get_value_unsigned()
        carry = total < 0
        r = MemoryValue(self.length, unsigned_int=total)
        overflow = False
        return r, carry, overflow

    def __add__(self, other):
        """
        Add, adds the value of two MemoryValues to each other
        Also supports adding integer values to the result
        :param other:
        :return:
        """
        if isinstance(other, MemoryValue):
            total_value = self.get_value_unsigned() + other.get_value_unsigned()
            n = MemoryValue(self.length)
            n.set_value_unsigned_int(total_value)
            return n
        elif isinstance(other, int):
            total_value = self.get_value_signed() + other
            n = MemoryValue(self.length)
            n.set_value_signed_int(total_value)
            return n
        return NotImplemented

    def __sub__(self, other):
        """
        Subtracts the value of two memory values from each other
        :param other:
        :return:
        """
        if isinstance(other, MemoryValue):
            val = self.get_value_unsigned() - other.get_value_unsigned()
            n = MemoryValue(self.length)
            n.set_value_unsigned_int(mask_value_for_length(self.length, val))
            return n
        elif isinstance(other, int):
            val = self.get_value_unsigned() - other
            n = MemoryValue(self.length)
            n.set_value_unsigned_int(mask_value_for_length(self.length, val))
            return n
        return NotImplemented

    def __gt__(self, other):
        """
        Greater than
        :param other:
        :return:
        """
        if isinstance(other, MemoryValue):
            return self.get_value_signed() > other.get_value_signed()
        elif isinstance(other, int):
            return self.get_value_signed() > other
        return NotImplemented

    def __lt__(self, other):
        """
        Less than
        :param other:
        :return:
        """
        if isinstance(other, MemoryValue):
            return self.get_value_signed() < other.get_value_signed()
        elif isinstance(other, int):
            return self.get_value_signed() < other
        return NotImplemented

    def __le__(self, other):
        """
        Less than or equals
        :param other:
        :return:
        """
        if isinstance(other, MemoryValue):
            return self.get_value_signed() <= other.get_value_signed()
        elif isinstance(other, int):
            return self.get_value_signed() <= other
        return NotImplemented

    def __ne__(self, other):
        """
        Not equal
        :param other:
        :return:
        """
        if isinstance(other, MemoryValue):
            return self.get_value_signed() != other.get_value_signed()
        elif isinstance(other, int):
            return self.get_value_signed() != other
        return NotImplemented

    def __ge__(self, other):
        """
        Greater or equal
        :param other:
        :return:
        """
        if isinstance(other, MemoryValue):
            return self.get_value_signed() >= other.get_value_signed()
        elif isinstance(other, int):
            return self.get_value_signed() >= other
        return NotImplemented

    def __str__(self):
        """
        to str, show the hex representation
        :return:
        """
        return '{1} MemoryValue {0:16b}'.format(self.unsigned_value, self.length.name)

    def __bytes__(self):
        """
        Get the bytes representation of this
        :return:
        """
        return self.unsigned_value.to_bytes(self.length.get_number_of_bytes(), byteorder='big', signed=False)

    def lsl(self, other):
        """
        logical shift left, allows for the msb to be set when shifted left
        :param other:
        :return:
        """
        if isinstance(other, MemoryValue):
            # shift the signed value to the left
            # preserve the sign
            val = self.get_value_unsigned() << other.get_value_signed()
            n = MemoryValue(self.length)
            n.set_value_unsigned_int(val)
            return n
        elif isinstance(other, int):
            val = self.get_value_unsigned() << other
            n = MemoryValue(self.length)
            n.set_value_unsigned_int(val)
            return n
        return NotImplemented

    def lsr(self, other):
        """
        logical shift right, the msb will always be 0
        :param other:
        :return:
        """
        if isinstance(other, MemoryValue):
            # shift the signed value to the left
            # preserve the sign
            val = self.get_value_unsigned() >> other.get_value_signed()
            n = MemoryValue(self.length)
            n.set_value_unsigned_int(val)
            return n
        elif isinstance(other, int):
            val = self.get_value_unsigned() >> other
            n = MemoryValue(self.length)
            n.set_value_unsigned_int(val)
            return n
        return NotImplemented

    def __lshift__(self, other):
        """
        Arithmetic left shift operator, sign of the result will be preserved
        :param other: an int or MemoryValue representing how much to shift the value of this by
        :return:
        """
        if isinstance(other, MemoryValue):
            # shift the signed value to the left
            # preserve the sign
            val = self.get_value_signed() << other.get_value_signed()
            n = MemoryValue(self.length)
            n.set_value_signed_int(val)
            return n
        elif isinstance(other, int):
            val = self.get_value_signed() << other
            n = MemoryValue(self.length)
            n.set_value_signed_int(val)
            return n
        return NotImplemented

    def __rshift__(self, other):
        """
        Arithmetic right shift operator, sign of the result will be preserved
        :param other: an int or MemoryValue representing how much to shift the value of this by
        :return:
        """
        # need to deal with this at a bit level, so doing it later
        if isinstance(other, MemoryValue):
            # shift the signed value to the left
            # preserve the sign
            val = self.get_value_signed() >> other.get_value_signed()
            n = MemoryValue(self.length)
            n.set_value_signed_int(val)
            return n
        elif isinstance(other, int):
            val = self.get_value_signed() >> other
            n = MemoryValue(self.length)
            n.set_value_signed_int(val)
            return n
        return NotImplemented

    def __xor__(self, other):
        """
        XOR operator
        :param other:
        :return:
        """
        if isinstance(other, MemoryValue):
            # need to xor the bytes, and not with the signed value
            val = self.unsigned_value ^ other.unsigned_value
            n = MemoryValue(self.length)
            n.set_value_unsigned_int(val)
            return n
        elif isinstance(other, int):
            # can do a lazy xor by using a signed value
            val = self.get_value_signed() ^ other
            n = MemoryValue(self.length)
            n.set_value_signed_int(val)
            return n
        return NotImplemented

    def __invert__(self):
        """
        Not operator
        :return:
        """
        # flip all of the bits and set the value
        mask = 0xFF
        if self.length is OpSize.WORD:
            mask = 0xFFFF
        elif self.length is OpSize.LONG:
            mask = 0xFFFFFFFF
        # xor w/ the mask to invert the value

        n = MemoryValue(self.length)
        n.set_value_unsigned_int(self.unsigned_value ^ mask)

        return n

    def __or__(self, other):
        """
        bitwise or
        :param other:
        :reeturn:
        """
        if isinstance(other, MemoryValue):
            # need to or the bytes, and not with the signed value
            val = self.unsigned_value | other.unsigned_value
            n = MemoryValue(self.length)
            n.set_value_unsigned_int(val)
            return n
        elif isinstance(other, int):
            # can do a lazy or by using a signed value
            val = self.get_value_signed() | other
            n = MemoryValue(self.length)
            n.set_value_unsigned_int(val)
            return n
        return NotImplemented

    def __and__(self, other):
        """
        bitwise and
        :param other:
        :return:
        """
        if isinstance(other, MemoryValue):
            # need to and the bytes, and not with the signed value
            val = self.unsigned_value & other.unsigned_value
            n = MemoryValue(self.length)
            n.set_value_unsigned_int(val)
            return n
        elif isinstance(other, int):
            # can do a lazy and by using a signed value
            val = self.get_value_signed() & other
            n = MemoryValue(self.length)
            n.set_value_unsigned_int(val)
            return n
        return NotImplemented

    def __floordiv__(self, other):
        """
        Floor div
        :param other:
        :return:
        """
        if isinstance(other, MemoryValue):
            val = self.get_value_signed() // other.get_value_signed()
            n = MemoryValue(self.length)
            n.set_value_unsigned_int(val)
            return n
        elif isinstance(other, int):
            val = self.get_value_signed() // other
            n = MemoryValue(self.length)
            n.set_value_unsigned_int(val)
            return n
        return NotImplemented

    def __mul__(self, other):
        """
        Multiply
        :param other:
        :return:
        """
        if isinstance(other, MemoryValue):
            val = self.get_value_signed() * other.get_value_signed()
            n = MemoryValue(self.length)
            n.set_value_unsigned_int(val)
            return n
        elif isinstance(other, int):
            val = self.get_value_signed() * other
            n = MemoryValue(self.length)
            n.set_value_unsigned_int(val)
            return n
        return NotImplemented

    def __mod__(self, other):
        """
        Mod
        :param other:
        :return:
        """
        if isinstance(other, MemoryValue):
            val = self.get_value_signed() % other.get_value_signed()
            n = MemoryValue(self.length)
            n.set_value_unsigned_int(val)
            return n
        elif isinstance(other, int):
            val = self.get_value_signed() % other
            n = MemoryValue(self.length)
            n.set_value_unsigned_int(val)
            return n
        return NotImplemented

    def __pow__(self, power, modulo=None):
        """
        Power
        :param power:
        :param modulo:
        :return:
        """
        if isinstance(power, MemoryValue):
            val = pow(self.get_value_signed(), power.get_value_signed())
            n = MemoryValue(self.length)
            n.set_value_unsigned_int(val)
            return n
        elif isinstance(power, int):
            val = pow(self.get_value_signed(), power)
            n = MemoryValue(self.length)
            n.set_value_unsigned_int(val)
            return n
        return NotImplemented
