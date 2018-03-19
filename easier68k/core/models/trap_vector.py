"""
Trap Vector

Represents the data type used by the TRAP opcode
in ASM looks just like an immediate value
"""

from ..util.parsing import parse_literal

class TrapVector:
    pass

class TrapVector:

    def __init__(self, value: int):
        assert 0 <= value <= 0b1111
        self.value = value

    def __str__(self):
        return 'Vector {}'.format(self.value)

    def get_value(self) -> int:
        return self.value

    @staticmethod
    def parse(asm_str: str) -> TrapVector:
        """
        Parses a trap vector value from a string
        and returns a new TrapVector

        :param asm_str:
        :return:
        """
        asm_str = asm_str.lower().strip()

        assert asm_str[0] == '#'

        return TrapVector(parse_literal(asm_str[1:]))