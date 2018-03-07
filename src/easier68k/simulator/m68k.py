"""
Motorola 68k chip definition
"""

from .memory import Memory
from ..core.enum.register import Register

class M68K:
    def __init__(self):
        """
        Constructor
        """
        self.memory = Memory()

        # todo how would we specify that we print from
        # stdin and stdout or a file, or whatever else
        # unsure of the best way to this currently
        # may resort to console output
        self.input_stream = 'todo???'
        self.output_stream = 'todo???'

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


    def run(self):
        """
        Starts the automatic execution
        :return:
        """

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
