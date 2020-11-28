from abc import abstractproperty
from .opcode_assembler import OpCodeAssembler
from .binary_prefix_tree import BinaryPrefixTree
from .condition import Condition
# from .opcode_base import (
#     OpCodeBase,
#     OpCodeAdd,
#     OpCodeSub,
#     OpCodeOr,
#     OpCodeAnd,
# )
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
    ("rts", 0b0100_1110_0111_0101),
    ("trapv", 0b0100_1110_0111_0110),
    ("rtr", 0b0100_1110_0111_0111),
    ("illegal", 0b0100_1010_1111_1100),
    ("simhalt", 0xffff)
    # todo, the rest of the word opcode assemblers (if any?)
]

BYTE_OPCODE_ASSEMBLER_DATA = [
    # opcode, byte
    ("ori", 0b0000_0000),
    ("andi", 0b0000_0010),
    ("subi", 0b0000_0100),
    ("addi", 0b0000_0110),
    ("eori", 0b0000_1010),
    ("cmpi", 0b0000_1100),
    ("negx", 0b0100_0000),
    ("clr", 0b0100_0010),
    ("neg", 0b0100_0100),
    ("not", 0b0100_0110),
    ("tst", 0b0100_1010),
    # todo, the rest of the byte opcode assemblers
]

FOUR_BIT_ASSEMBLER_BASE_DATA = [
    # OpCode, First 4 bits
    # and assumes two operands
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
        self._prefix = word

    @abstractproperty
    def prefix(self):
        return self._prefix

    @property
    def literal_prefix(self):
        return self.prefix, 16
    
    @property
    def format(self):
        return [(16, 0, self.prefix)]

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

class MoveAssembler(OpCodeAssembler):
    def __init__(self):
        super().__init__("move")

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
    def __init__(self):
        super().__init__("btst")

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

class CmpAssembler(OpCodeAssembler):
    def __init__(self):
        super().__init__("cmp")

    @property
    def literal_prefix(self):
        return 0b1011, 4
    
    @property
    def format(self):
        return [
            (4, 12, 0b1011),
            (3, 9, None), # Dn
            (3, 6, None), # S
            (3, 3, None), # M
            (3, 0, None), # Xn
        ]

class TrapAssembler(OpCodeAssembler):
    def __init__(self):
        super().__init__("trap")

    @property
    def literal_prefix(self):
        return 0b010011100100, 12
    
    @property
    def format(self):
        return [
            (12, 4, 0b010011100100),
            (4, 0, None), # Vector
        ]

class LeaAssembler(OpCodeAssembler):
    def __init__(self):
        super().__init__("lea")

    @property
    def literal_prefix(self):
        return 0b0100, 4
    
    @property
    def format(self):
        return [
            (4, 12, 0b0100),
            (3, 9, None), # Address Register Dest
            (3, 6, 0b111),
            (3, 3, None), # src ea mode
            (3, 0, None), # src ea register
        ]


# the trie I use for the assemblers might fall down here...
# need to make sure it tries all of the possible matches that it hass
class AslAssembler(OpCodeAssembler):
    def __init__(self):
        super().__init__("asl")
    
    @property
    def literal_prefix(self):
        return 0b1110, 4
    
    @property
    def format(self):
        return [
            (4, 12, 0b1110),
            (3, 9, None), # count/register
            (1, 8, 1), # direction 0 = right, 1 left
            (2, 6, None), # size
            (1, 5, None), # i/r, 0 = imm shift, 1 = register shift
            (2, 3, 0b00),
            (3, 0, None), # register
        ]

class AsrAssembler(OpCodeAssembler):
    def __init__(self):
        super().__init__("asr")
    
    @property
    def literal_prefix(self):
        return 0b1110, 4
    
    @property
    def format(self):
        return [
            (4, 12, 0b1110),
            (3, 9, None), # count/register
            (1, 8, 0), # direction 0 = right, 1 left
            (2, 6, None), # size
            (1, 5, None), # i/r, 0 = imm shift, 1 = register shift
            (2, 3, 0b00),
            (3, 0, None), # register
        ]

class BranchAssembler(OpCodeAssembler):
    opcodes = [
        "bhi", "bls", "bcc", "bcs", "bne", "beq", "bvc", "bvs", "bpl", "bmi", "blt", "bgt", "ble"
    ]
    def __init__(self, condition: Condition):
        op_name = f"b{condition.name.lower()}"
        self.condition = condition
        self.prefix = 0b0110 << 4 | self.condition.value
        print(f'condition {self.condition} prefix {self.prefix:8b}')
        super().__init__(op_name)
    
    @property
    def literal_prefix(self):
        return self.prefix, 8
    
    @property
    def format(self):
        return [
            (4, 12, 0b0110), # prefix for all branches
            (4, 8, None), # condition
            (8, 0, None), # 8-bit displacement
            # TODO: will need to expand this to peek at the next two words
            # for 16 bit and 32 bit displacements
        ]

NON_PATTERN_ASSEMBLERS = [
    # the assemblers which do not conform to a specific pattern, like the word/byte/4 bit prefixes
    MoveAssembler(),
    BtstAssembler(),
    CmpAssembler(),
    TrapAssembler(),
    LeaAssembler(),
    AslAssembler(),
    AsrAssembler(),
]

for _, value in vars(Condition).items():
    if not isinstance(value, Condition): continue
    NON_PATTERN_ASSEMBLERS.append(BranchAssembler(value))

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

    result = words + byte_prefix + four_bit + NON_PATTERN_ASSEMBLERS
    result_dict = {x.get_opcode(): x for x in result}

    # workaround
    result_dict["bra"] = result_dict["bt"]
    return result_dict


assemblers = generate_assembler_list()
