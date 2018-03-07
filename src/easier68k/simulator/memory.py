"""
Represents all of the memory for the 68k
This should be able to be serialized/deserialized
and accessed completely
"""

from ..core.enum.register import Register
from ..core.enum.condition import Condition
from ..core.enum.condition_status_code import ConditionStatusCode
from ..core.enum.system_status_code import SystemStatusCode

class UnalignedMemoryAccessError(Exception):
    pass

class OutOfBoundsMemoryError(Exception):
    pass

class Memory:
    Byte = 1
    Word = 2
    Long = 4

    def __validateLocation(self, size: int, location: int):
        """
        Helper function which throws an error if the location is either
        not aligned or out of bounds
        """
        if(location % size != 0):
            raise UnalignedMemoryAccessError
        if(location < 0 or location+size > len(self.memory)):
            raise OutOfBoundsMemoryError

    def __init__(self):
        """
        Constructor
        """

        # all of the memory that is stored by the device
        # 16777216 = 2^24
        # it is the number of bytes easy68K uses.
        self.memory = bytearray(16777216)

    def save_memory(self, file):
        """
        saves the raw memory into the designated file
        NOTE: file must be opened as binary or this won't work
        """
        file.write(self.memory)

    def load_memory(self, file):
        """
        Loads the raw memory from the designated file
        This includes programs
        NOTE: file must be opened as binary or this won't work
        """
        self.memory = bytearray(file.read())

    def get(self, size: int, location: int) -> bytearray:
        """
        gets the memory at the given location index of size
        """
        self.__validateLocation(size, location)
        return self.memory[location:location+size]

    def set(self, size: int, location: int, value: bytearray):
        """
        sets the memory at the given location index of size
        """
        self.__validateLocation(size, location)
        if(len(value) != size):
            raise AssignWrongMemorySizeError
        self.memory[location:location+size] = value
