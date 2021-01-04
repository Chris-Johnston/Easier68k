from typing import Optional
from abc import ABC, abstractmethod, abstractproperty
# from .opcode_base import OpCodeBase

class OpCodeAssembler():
    def __init__(self, opcode, immediates: Optional[list] = None):
        self._opcode = opcode

        # going to assume that these are word values, hopefully this doesn't come back to
        # haunt me?
        # if it does, could change this into MemoryValue
        self.immediate = immediates or list()

    @abstractproperty
    def literal_prefix(self) -> int:
        pass

    @abstractproperty
    def format(self) -> list:
        pass

    def _get_bitmask(self, num_bits: int) -> int:
        return (1 << num_bits) - 1

    def is_match(self, word: int) -> bool:
        # checks if the given word value is a match
        
        # make a mask from all of the literal bits
        # and check that bitwise & with the mask is the same
        literal_mask = 0
        literal_compare = 0
        for length, offset, literal in self.format:
            if literal is not None:
                literal_compare |= literal << offset
                mask = (1 << length) - 1
                literal_mask |= mask << offset

        # print(self.format)
        # print(f"word {word:016b}")
        # print(f"lcmp {literal_compare:016b}")
        # print(f"mask {literal_mask:016b} {self.get_opcode()}")
        # print(f"     {word & literal_mask:016b}")
        # print("---------\n")
        return (word & literal_mask) == literal_compare
        # return (word ^ literal_mask) == 0
    
    def assemble(self, values: list) -> int:
        # assemble using the list of values 
        values_index = 0
        word = 0
        assert values is not None, "Values must not be None"
        print("values:", values)

        print(self.format)
        for size, offset, literal in self.format:
            print("size", size, "offset", offset, "literal", literal)
            if literal is not None:
                word |= literal << offset
            else:
                value = values[values_index] & self._get_bitmask(size)
                word |= value << offset
                values_index += 1
            print(f"word: {word:8b}")
        return word
    
    def assemble_immediate(self, values: list) -> list:
        # assembles all of the values including the immediates
        op = self.assemble(values)
        l = [op]
        if self.immediate:
            l.append(self.immediate)
        return l

    def disassemble_values(self, word) -> list:
        # gets the values in the order of the instruction
        # this should be used to build the actual instruction after
        from .memory_value import MemoryValue
        if isinstance(word, MemoryValue):
            word = word.get_value_unsigned()

        assert self.is_match(word), f"The word {word} did not match with the opcode {self._opcode}"
        values = []

        for size, offset, literal in self.format:
            # value is dynamic, so we care about it
            if literal is None:
                # make a mask for the size of value specified
                # shift this mask by offset bits
                value_mask = self._get_bitmask(size) << offset
                # mask this value from the word, shift back
                value = (word & value_mask) >> offset
                values.append(value)
        return values
    
    @abstractmethod
    def get_opcode(self): # -> str:
        return self._opcode
