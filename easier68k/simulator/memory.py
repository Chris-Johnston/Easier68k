"""
Represents all of the memory for the 68k
This should be able to be serialized/deserialized
and accessed completely
"""

from ..core.enum.register import Register
from ..core.enum.condition import Condition
from ..core.enum.condition_status_code import ConditionStatusCode
from ..core.enum.system_status_code import SystemStatusCode
from ..core.enum.floating_point_exception import FloatingPointException
from ..core.enum.floating_point_condition_code import FloatingPointConditionCode
from ..core.enum.floating_point_accured_exception import FloatingPointAccuredException

class Memory:
	Byte = 1
	Word = 2
	Long = 4
	
	def __validateLocation(self, size, location):
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

    def dump_memory(self):
        """
        Dumps the contents of the memory to a binary blob
        :return:
        """
        pass

    def load_memory(self, binblob):
        """
        Loads the contents of the memory from a
        binary blob

        This includes programs
        """
        pass

    def get(self, size, location):
        """
        gets the memory at the given location index of size
        """
		self.__validateLocation(size, location)
		return self.memory[location:location+size]

	def set(self, size, location, value):
		"""
		sets the memory at the given location index of size
		"""
		self.__validateLocation(size, location)
		if(len(value) != size):
			raise AssignWrongMemorySizeError
		self.memory[location:location+size] = value

