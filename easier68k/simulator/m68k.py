"""
Motorola 68k chip definition
"""

from . import *

class M68K:
    def __init__(self):
        """
        Constructor
        """
        self.memory = easier68k.simulator.memory.Memory()

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
