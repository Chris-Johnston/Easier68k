"""
Represents all of the memory for the 68k
This should be able to be serialized/deserialized
and accessed completely
"""

from ..core.enum.register import Register
from ..core.enum.condition import Condition
from ..core.enum.condition_status_code import ConditionStatusCode
from ..core.enum.system_status_code import SystemStatusCode
from ..core.models.list_file import ListFile
import typing
from ..core.models.memory_value import MemoryValue
from ..core.enum.op_size import OpSize

class UnalignedMemoryAccessError(Exception):
    pass

class OutOfBoundsMemoryError(Exception):
    pass

class AssignWrongMemorySizeError(Exception):
    pass

class Memory:

    def __validateLocation(self, size: OpSize, location: int):
        """
        Helper function which throws an error if the location is either
        not aligned or out of bounds
        """
        if not isinstance(size, OpSize):
            size = OpSize(size)
        if(location % size.get_number_of_bytes() != 0):
            raise UnalignedMemoryAccessError
        if(location < 0 or (location + size.get_number_of_bytes()) > len(self.memory)):
            raise OutOfBoundsMemoryError

    def __init__(self):
        """
        Constructor
        """

        # all of the memory that is stored by the device
        # 16777216 = 2^24
        # it is the number of bytes easy68K uses.
        self.memory = bytearray(16777216)

    def save_memory(self, file : typing.BinaryIO):
        """
        saves the raw memory into the designated file
        NOTE: file must be opened as binary or this won't work
        """
        file.write(self.memory)

    def load_memory(self, file : typing.BinaryIO):
        """
        Loads the raw memory from the designated file
        This includes programs
        NOTE: file must be opened as binary or this won't work
        """
        self.memory = bytearray(file.read())


    def load_list_file(self, list_file: ListFile):
        """
        Load List File

        load the contents of a list file into memory
        using the locations specified inside of the list file
        starting location, registers, etc... (anything
        which is not data) is ignored
        :param list_file:
        :return:
        """

        # for all of the locations, load the contents into memory
        for key, value in list_file.data.items():
            # internally stored as a string for json compatibility
            # so convert back into an integer to represent the index
            location = int(key)

            # decode the data into a ByteArray
            # and then set it
            values = bytearray.fromhex(value)

            for i in range(0, len(values), 1):
                # set one byte at a time
                val = MemoryValue(OpSize.BYTE, bytes=values[i:i+1])
                self.set(OpSize.BYTE, location + i, val)

    def get(self, size: OpSize, location: int) -> MemoryValue:
        """
        gets the memory at the given location index of size
        """
        if not isinstance(size, OpSize):
            size = OpSize(size)
        self.__validateLocation(size, location)
        ret = MemoryValue(size)
        end = location + size.value
        b = None
        try:
            b = self.memory[location:end]
        except TypeError:
            pass
        ret.set_value_bytes(b)
        return ret

    def set(self, size: OpSize, location: int, value: MemoryValue):
        """
        sets the memory at the given location index of size
        """
        if not isinstance(value, MemoryValue):
            raise AssertionError("The value parameter must be of type MemoryValue")

        if not isinstance(size, OpSize):
            size = OpSize(size)

        self.__validateLocation(size, location)
        if value.get_size() != size:
            raise AssignWrongMemorySizeError
        self.memory[location:location+size.get_number_of_bytes()] = value.get_value_bytes()
