"""
Represents all of the memory for the 68k
This should be able to be serialized/deserialized
and accessed completely
"""

# import enums
from src.core.enum.register import Register
from src.core.enum.condition_status_code import ConditionStatusCode
from src.core.enum.system_status_code import SystemStatusCode


class Memory:

    def __init__(self):
        """
        Constructor
        """

        # how many bytes of memory to keep track of
        self.memory_size = 68000

        # all of the memory that is stored by the device
        # each location should represent a byte and no more
        self.memory = [ 0 for i in range(self.memory_size) ]

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

    def get_memory_value(self, location):
        """
        returns the word contained at the given
        memory location

        can convert these using the util conversion
        :param location:
        :return:
        """
        pass

    def set_memory_value_word(self, location, value):
        """
        sets the word value at the given location
        :param location:
        :param value:
        :return:
        """
        pass

    def set_memory_value_long(self, location, value):
        """
        sets the long value at the given location
        :param location:
        :param value:
        :return:
        """
        pass

    def set_memory_value_byte(self, location, value):
        """
        sets the byte value at the given location
        :param location:
        :param value:
        :return:
        """
        pass

    def get_register(self, register_number: Register):
        """
        Returns the contents of the given register D0-D7 A0-A7
        :param register_number:
        :return: The entire word contained inside the register
        """
        return 0

    def get_user_stack_pointer(self):
        return -1

    def get_program_counter(self):
        return -1

    def get_status_register(self):
        return -1

    def get_condition_code_register(self):
        """
        The condition code register is
        just the first byte of the status
        register
        :return:
        """
        return self.get_status_register() & 0xFF

    def get_condition_code(self, code: ConditionStatusCode):
        return (self.get_condition_code_register() & code) > 0

    def get_system_status_code(self, code: SystemStatusCode):
        return self.get_condition_code_register() & code
