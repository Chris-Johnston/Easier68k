from abc import ABC, abstractmethod, abstractproperty

class OpCodeAssembler(ABC):
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
        for _, offset, literal in self.format:
            if literal:
                literal_mask |= literal << offset

        return (word & literal_mask) == literal_mask
    
    def assemble(self, values: list) -> int:
        # assemble using the list of values 
        values_index = 0
        word = 0
        assert values, "Values must not be empty"

        for size, offset, literal in self.format:
            if literal:
                word |= literal << offset
            else:
                value = values[values_index] & self._get_bitmask(size)
                word |= value << offset
                values_index += 1
        return word

    def disassemble_values(self, word) -> list:
        # gets the values in the order of the instruction
        # this should be used to build the actual instruction after
        assert self.is_match(word)
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