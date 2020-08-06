from abc import abstractproperty
from .opcode_assembler import OpCodeAssembler
from .binary_prefix_tree import BinaryPrefixTree
from .opcode_base import (
    OpCodeBase,
    OpCodeAdd,
    OpCodeSub,
    OpCodeOr,
    OpCodeAnd,
)
# problem: having to import all of the opcode classes will add up quickly
# instead, maybe I could insteaad have get_opcode return a string literal which corresponds to the opcode
# also, instead of having one class for each type of assembler, we could have lists of classifications
# so that I'm not creating a million different classes for each type
# future cleanup: have consts for the opcodes to avoid magic strings/typos

WORD_OPCODE_ASSEMBLER_DATA = [
    # OpCode (will be converted to upper), Word
    ("reset", 0b0100_1110_0111_0000),
    ("nop", 0b0100_1110_0111_0000),
    ("stop", 0b0100_1110_0111_0010),
    ("rte", 0b0100_1110_0111_0011),
    # todo, do the rest
]

BYTE_OPCODE_ASSEMBLER_DATA = [
    # opcode, byte
    ("ori", 0b0000_0000),
]

FOUR_BIT_ASSEMBLER_BASE_DATA = [
    # OpCode, First 4 bits
    ("add", 0b1101),
    ("sub", 0b1001),
    ("and", 0b1100),
    ("or", 0b1000),
    # todo, do the rest
]

# base class that handles the case of 1 byte prefix, S, M, Xn
class BytePrefixOpCodeAssembler(OpCodeAssembler):
    def __init__(self, opcode, prefix):
        super().__init__(opcode)
        self._prefix = prefix

    @abstractproperty
    def prefix(self):
        return self._prefix

    @property
    def literal_prefix(self):
        return self.prefix, 8

    @property
    def format(self):
        return [
            (8, 8, self.prefix),
            (2, 6, None), # S
            (3, 3, None), # M
            (3, 0, None), # Xn
            ]

    def get_opcode(self):
        return self._opcode

class WordOpCodeAssembler(OpCodeAssembler):
    def __init__(self, opcode, word):
        super().__init__(opcode)
        self._word = word

    @abstractproperty
    def word_opcode(self):
        return self._word

    @property
    def literal_prefix(self):
        return self.word_opcode, 16
    
    @property
    def format(self):
        return [(16, 0, self.word_opcode)]

class RtsAssembler(WordOpCodeAssembler):
    @property
    def word_opcode(self):
        return 0b0100_1110_0111_0101

class TrapvAssembler(WordOpCodeAssembler):
    @property
    def word_opcode(self):
        return 0b0100_1110_0111_0110

class RtrAssembler(WordOpCodeAssembler):
    @property
    def word_opcode(self):
        return 0b0100_1110_0111_0111

class IllegalAssembler(WordOpCodeAssembler):
    @property
    def word_opcode(self):
        return 0b0100_1010_1111_1100

class OriAssembler(BytePrefixOpCodeAssembler):
    @property
    def prefix(self):
        return 0b0000_0000

class AndiAssembler(BytePrefixOpCodeAssembler):
    @property
    def prefix(self):
        return 0b0000_0010

class SubiAssembler(BytePrefixOpCodeAssembler):
    @property
    def prefix(self):
        return 0b0000_0100

class AddiAssembler(BytePrefixOpCodeAssembler):
    @property
    def prefix(self):
        return 0b0000_0110

class EoriAssembler(BytePrefixOpCodeAssembler):
    @property
    def prefix(self):
        return 0b0000_1010

class CmpiAssembler(BytePrefixOpCodeAssembler):
    @property
    def prefix(self):
        return 0b0000_1100

class NegxAssembler(BytePrefixOpCodeAssembler):
    @property
    def prefix(self):
        return 0b0100_0000

class ClrAssembler(BytePrefixOpCodeAssembler):
    @property
    def prefix(self):
        return 0b0100_0010

class NegAssembler(BytePrefixOpCodeAssembler):
    @property
    def prefix(self):
        return 0b0100_0100

class NotAssembler(BytePrefixOpCodeAssembler):
    @property
    def prefix(self):
        return 0b0100_0110

class TstAssembler(BytePrefixOpCodeAssembler):
    @property
    def prefix(self):
        return 0b0100_1010

class FourBitAssemblerBase(OpCodeAssembler):
    def __init__(self, opcode, prefix):
        super().__init__(opcode)
        self._prefix = prefix

    @abstractproperty
    def prefix(self):
        return self._prefix

    @property
    def literal_prefix(self):
        return self.prefix, 4
    
    @property
    def format(self):
        return [
            (4, 12, self.prefix),
            (3, 9, None), # Dn
            (1, 8, None), # D
            (2, 6, None), # S
            (3, 3, None), # M
            (3, 0, None), # Xn
        ]

class AndAssembler(FourBitAssemblerBase):
    @property
    def prefix(self):
        return 0b1100

    def get_opcode(self):
        return OpCodeAnd()

class OrAssembler(FourBitAssemblerBase):
    @property
    def prefix(self):
        return 0b1000

    def get_opcode(self):
        return OpCodeOr()

# TODO: should probably be consistent with prefixes or suffixes with "OpCode" and "Assembler"
# since <op>Assembler is here, but elsewhere it's OpCode<op>

class MoveAssembler(OpCodeAssembler):
    @property
    def literal_prefix(self):
        return 0b00, 2

    @property
    def format(self):
        return [
            (2, 14, 0b00), # literal
            (2, 12, None), # S
            (3, 9, None), # Xn
            (3, 6, None), # M
            (3, 3, None), # M
            (3, 0, None), # Xn
        ]

class BtstAssembler(OpCodeAssembler):
    @property
    def literal_prefix(self):
        return 0b0000100000, 10

    @property
    def format(self):
        return [
            (10, 6, 0b0000100000), # literal
            (3, 3, None), # M
            (3, 0, None), # Xn
        ]

def generate_assembler_list():
    """
    uses the constants in this file to generate a list of assemblers
    """
    # word prefix ones
    words = [WordOpCodeAssembler(opcode, word) for opcode, word in WORD_OPCODE_ASSEMBLER_DATA]

    # byte prefix ones
    byte_prefix = [BytePrefixOpCodeAssembler(opcode, byte) for opcode, byte in BYTE_OPCODE_ASSEMBLER_DATA]

    # 4 bit prefix ones
    four_bit = [FourBitAssemblerBase(opcode, prefix) for opcode, prefix in FOUR_BIT_ASSEMBLER_BASE_DATA]

    result = words + byte_prefix + four_bit
    # print("assemblers:", len(result))
    # for x in result:
    #     print(f"{x.get_opcode()} - {x}")
    result_dict = {x.get_opcode(): x for x in result}
    return result_dict

# assemblers = [
#     OriAssembler(),
#     AndiAssembler(),
#     SubiAssembler(),
#     AddiAssembler(),
#     EoriAssembler(),
#     CmpiAssembler(),
#     NegxAssembler(),
#     ClrAssembler(),
#     NegAssembler(),
#     NotAssembler(),
#     TstAssembler(),
#     AddAssembler(),
#     SubAssembler(),
#     AndAssembler(),
#     OrAssembler(),
#     MoveAssembler(),
#     BtstAssembler(),
#     ResetAssembler(),
#     NopAssembler(),
#     StopAssembler(),
#     RteAssembler(),
#     RtsAssembler(),
#     TrapvAssembler(),
#     RtrAssembler(),
#     IllegalAssembler(),
#     ]

assemblers = generate_assembler_list()

# if __name__ == "__main__":

#     tree = BinaryPrefixTree(assemblers)

#     add = tree.get_assembler(0b1101_0000_0000_0000)
#     print('this should be add:', add)

#     print('this should be BTST:', tree.get_assembler(0b0000_1000_0000_0000))
#     print('this should be None:', tree.get_assembler(0b1111_0000_0000_0000))
#     print('this should be None:', tree.get_assembler(0b0111_0000_0000_0000))

#     for x in range(0, 0b1111_1111):
#         asm = tree.get_assembler(x << 8)
#         if asm is not None:
#             print('found', asm, 'at', bin(x))
#     exit(0)

#     add = AddAssembler()
#     example_word = 0b1101_1110_1100_0111
#     assert add.is_match(example_word)

#     values = add.disassemble_values(example_word)
#     print(values)

#     out_word = add.assemble(values)
#     print(bin(out_word))

#     assert example_word == out_word
    