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

# base class that handles the case of 1 byte prefix, S, M, Xn
class BytePrefixOpCodeAssembler(OpCodeAssembler):
    @abstractproperty
    def prefix(self):
        pass

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

class WordOpCodeAssembler(OpCodeAssembler):
    @abstractproperty
    def opcode(self):
        pass

    @property
    def literal_prefix(self):
        return self.opcode, 16
    
    @property
    def format(self):
        return [(16, 0, self.opcode)]

class ResetAssembler(WordOpCodeAssembler):
    @property
    def opcode(self):
        return 0b0100_1110_0111_0000

class NopAssembler(WordOpCodeAssembler):
    @property
    def opcode(self):
        return 0b0100_1110_0111_0001

class StopAssembler(WordOpCodeAssembler):
    @property
    def opcode(self):
        return 0b0100_1110_0111_0010

class RteAssembler(WordOpCodeAssembler):
    @property
    def opcode(self):
        return 0b0100_1110_0111_0011

class RtsAssembler(WordOpCodeAssembler):
    @property
    def opcode(self):
        return 0b0100_1110_0111_0101

class TrapvAssembler(WordOpCodeAssembler):
    @property
    def opcode(self):
        return 0b0100_1110_0111_0110

class RtrAssembler(WordOpCodeAssembler):
    @property
    def opcode(self):
        return 0b0100_1110_0111_0111

class IllegalAssembler(WordOpCodeAssembler):
    @property
    def opcode(self):
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
    @abstractproperty
    def prefix(self):
        pass

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

class AddAssembler(FourBitAssemblerBase):
    @property
    def prefix(self):
        return 0b1101

    def get_opcode(self):
        return OpCodeAdd()

class SubAssembler(FourBitAssemblerBase):
    @property
    def prefix(self):
        return 0b1001

    def get_opcode(self):
        return OpCodeSub()

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

assemblers = [
    OriAssembler(),
    AndiAssembler(),
    SubiAssembler(),
    AddiAssembler(),
    EoriAssembler(),
    CmpiAssembler(),
    NegxAssembler(),
    ClrAssembler(),
    NegAssembler(),
    NotAssembler(),
    TstAssembler(),
    AddAssembler(),
    SubAssembler(),
    AndAssembler(),
    OrAssembler(),
    MoveAssembler(),
    BtstAssembler(),
    ResetAssembler(),
    NopAssembler(),
    StopAssembler(),
    RteAssembler(),
    RtsAssembler(),
    TrapvAssembler(),
    RtrAssembler(),
    IllegalAssembler(),
    ]

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
    