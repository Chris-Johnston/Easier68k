"""
Used by m68k to handle stepping through actions
"""


class Clock():
    def __init__(self):
        """
        Constructor
        """

        # automatically advance to the next cycle
        self.auto = True

        # todo add a handler for advancing the clock
