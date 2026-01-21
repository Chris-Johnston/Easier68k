from enum import IntEnum
from .parsing import parse_literal


class TrapVectors(IntEnum):
    IO = 15

    @staticmethod
    def parse(asm_str: str):
        """
        Parses a trap vector value from a string
        and returns a new TrapVector

        :param asm_str:
        :return:
        """
        asm_str = asm_str.lower().strip()

        assert asm_str[0] == '#'

        return TrapVectors(parse_literal(asm_str[1:]))