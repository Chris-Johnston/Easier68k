"""
Motorola 68k chip definition
"""

from .memory import Memory
from ..core.enum.register import Register
from ..core.enum.condition_status_code import ConditionStatusCode

MAX_MEMORY_LOCATION = 16777216  # 2^24

class M68K:
    def __init__(self):
        """
        Constructor
        """
        self.memory = Memory()

        self.clock_auto_cycle = True
        self._clock_cycles = 0

        # todo add events for each clock cycle
        # this is necessary for implementing breakpoints
        # and watches for value changes

        # set up the registers to their default values
        self.registers = {}
        self.__init_registers()

    def __init_registers(self):
        """
        Set the registers to their default values
        :return:
        """

        # loop through all of the 'normal' registers which are just 32 bits / 4 bytes long
        normal_registers = [Register.D0, Register.D1, Register.D2, Register.D3, Register.D4, Register.D5, Register.D6,
                            Register.D6, Register.D7, Register.A0, Register.A1, Register.A2, Register.A3, Register.A4,
                            Register.A5, Register.A6, Register.A7, Register.PC ]
        for register in normal_registers:
            self.registers[register] = bytearray(4)

        # set up all of the odd registers (in this case, just the Condition Code Register)
        # which just uses 5 bits out of the lowermost byte (do we want to allocate it an entire word instead?)
        self.registers[Register.ConditionCodeRegister] = bytearray(1)

    def get_register(self, register: Register) -> bytearray:
        """
        Gets the entire value of a register
        :param register:
        :return:
        """
        return self.registers[register]

    def get_program_counter_value(self) -> int:
        """
        Gets the 32-bit integer value for the program counter value
        :return:
        """
        # convert the contents of the byte array to hex, and then convert
        # that into an int
        return int(self.registers[Register.PC].hex(), 16)

    def set_program_counter_value(self, new_value: int):
        """
        Sets the value of the program counter
        Must be a non negative integer that is less than the maximum location size
        :param new_value:
        :return:
        """
        assert 0 <= new_value < MAX_MEMORY_LOCATION, 'The value of the program counter must be non-negative and less than the maximum bound.'

        # convert the new value into a byte array of len 4, then update the PC
        # register to that new value
        self.registers[Register.PC] = bytearray(new_value.to_bytes(4, 'big'))

    def get_condition_status_code(self, code: ConditionStatusCode) -> bool:
        """
        Gets the status of a code from the Condition Code Register
        :param code:
        :return:
        """
        ccr = self.get_register(Register.CCR)
        # ccr is only 1 byte, bit mask away the bit being looked for
        return (ccr[0] & code) > 0


    def run(self):
        """
        Starts the automatic execution
        :return:
        """
        pass

    def step_clock(self):
        """
        Increments the clock by a single cycle
        :return:
        """
        pass

    def step_instruction(self):
        """
        Increments the clock until the program
        counter increments
        :return:
        """
        pass

    def reload_execution(self):
        """
        restarts execution of the program
        up to the current program counter location
        :return:
        """
        pass

    def get_cycles(self):
        """
        Returns how many clock cycles have been performed
        :return:
        """
        return self._clock_cycles

    def clear_cycles(self):
        """
        Resets the count of clock cycles
        :return:
        """
        self._clock_cycles = 0
