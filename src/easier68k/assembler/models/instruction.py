"""
Instruction

represents a single instruction in assembly
"""

class Instruction():
    def __init__(self):

        # what opcode mnemonic
        # this would be 'MOVE' or 'NOP' or whatever
        self.opcode = None

        # what size (if specified)
        # 'B' 'W' 'L' or None
        self.size = None

        # list of all of the parameters after the opcode
        # these would be the immediate values or registers or whatever else
        self.params = []