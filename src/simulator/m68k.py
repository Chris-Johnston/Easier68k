"""
Motorola 68k chip definition
"""

from .memory import Memory

class M68K:

    def __init__(self):
        """
        Constructor
        """
        self.memory = Memory()

        self.clock_auto_cycle = True
        self._clock_cycles = 0

        #todo add events for each clock cycle
        # this is necessary for implementing breakpoints
        # and watches for value changes

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