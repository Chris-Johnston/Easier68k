"""
Represents all of the memory for the 68k
This should be able to be serialized/deserialized
and accessed completely
"""

# import enums
from src.core.enum.register import Register
from src.core.enum.condition_status_code import ConditionStatusCode
from src.core.enum.system_status_code import SystemStatusCode
from src.core.enum.floating_point_exception import FloatingPointException
from src.core.enum.floating_point_condition_code import FloatingPointConditionCode
from src.core.enum.floating_point_accured_exception import FloatingPointAccuredException


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

    # see page 1-4 of the M68000PRM
    def get_floating_point_control_register(self):
        # 16 bit
        return -1

    # consider making a floating point status
    # register class for all of this?

    # utils for the floating point control register
    def get_floating_point_exception_status(self, exception: FloatingPointException):
        return (self.get_floating_point_control_register() & exception) > 0

    def get_floating_point_status_register(self):
        return -1

    def get_floating_point_condition_code(self, code: FloatingPointConditionCode):
        return (self.get_floating_point_status_register() & code) > 0

    def get_floating_point_status_register_quotient(self):
        """ See figure 1-5 FPSR Quotient Code Byte """
        return self.get_floating_point_status_register() & (0b1111111 << 16)

    def get_floating_point_status_register_quotient_sign(self):
        return (self.get_floating_point_status_register() & (1 << 23)) >> 23

    def get_floating_point_status_register_accured_exception(self, code: FloatingPointAccuredException):
        return (self.get_floating_point_status_register() & code) > 0

    def get_floating_point_instruction_address_register(self):
        return -1
