"""
Op Size Enum
Holds the values for various binary translations of size codes

>>> MoveSize.BYTE
<MoveSize.BYTE: 1>

>>> MoveSize.LONG
<MoveSize.LONG: 2>

>>> MoveSize.WORD
<MoveSize.WORD: 3>

>>> MoveSize(0b01)
<MoveSize.BYTE: 1>

>>> MoveSize(0b11)
<MoveSize.WORD: 3>

>>> MoveSize(0b10)
<MoveSize.LONG: 2>

>>> MoveSize.parse('B')
<MoveSize.BYTE: 1>

>>> MoveSize.parse('w')
<MoveSize.WORD: 3>

>>> MoveSize.parse('L')
<MoveSize.LONG: 2>

>>> Size(0)
<Size.BYTE: 0>

>>> Size(1)
<Size.WORD: 1>

>>> Size(2)
<Size.LONG: 2>

>>> Size.BYTE
<Size.BYTE: 0>

>>> Size.WORD
<Size.WORD: 1>

>>> Size.LONG
<Size.LONG: 2>

>>> Size.parse('B')
<Size.BYTE: 0>

>>> Size.parse('w')
<Size.WORD: 1>

>>> Size.parse('l')
<Size.LONG: 2>

>>> SingleBitSize.WORD
<SingleBitSize.WORD: 0>

>>> SingleBitSize.LONG
<SingleBitSize.LONG: 1>

>>> SingleBitSize.parse('l')
<SingleBitSize.LONG: 1>

>>> SingleBitSize.parse('w')
<SingleBitSize.WORD: 0>

>>> SingleBitSize.parse('b')

"""

from enum import IntEnum, Enum

# forward declaration so that types can return correctly
class MoveSize(IntEnum):
    pass

class OpSize(Enum):
    pass

class MoveSize(IntEnum):
    """
    Represents the "Big S" sizes (dark purple on this chart: http://goldencrystal.free.fr/M68kOpcodes-v2.3.pdf)
    """
    BYTE = 0b01
    WORD = 0b11
    LONG = 0b10

    @staticmethod
    def parse(code: chr) -> MoveSize:
        code = code.upper()
        if code == 'B':
            return MoveSize.BYTE
        if code == 'W':
            return MoveSize.WORD
        if code == 'L':
            return MoveSize.LONG

    @staticmethod
    def from_op_size(opsize: OpSize) -> MoveSize:
        """
        Converts an OpSize into a MoveSize
        :param opsize:
        :return:
        """

        if opsize is OpSize.BYTE:
            return MoveSize.BYTE
        if opsize is OpSize.WORD:
            return MoveSize.WORD
        if opsize is OpSize.LONG:
            return MoveSize.LONG

    def to_op_size(self) -> OpSize:
        """
        converts back to the op size
        :return:
        """
        if self is MoveSize.BYTE:
            return OpSize.BYTE
        if self is MoveSize.WORD:
            return OpSize.WORD
        if self is MoveSize.LONG:
            return OpSize.LONG

# forward declaration so that types can return correctly
class Size(IntEnum):
    pass

class Size(IntEnum):
    """
    Represents the "Small S" sizes (light purple on this chart: http://goldencrystal.free.fr/M68kOpcodes-v2.3.pdf)
    """
    BYTE = 0b00
    WORD = 0b01
    LONG = 0b10

    @staticmethod
    def parse(code: chr) -> Size:
        code = code.upper()
        if code == 'B':
            return Size.BYTE
        if code == 'W':
            return Size.WORD
        if code == 'L':
            return Size.LONG

class SingleBitSize(IntEnum):
    pass

class SingleBitSize(IntEnum):
    """
    Represents the single bit sizes (medium purple on this chart: http://goldencrystal.free.fr/M68kOpcodes-v2.3.pdf)
    """
    WORD = 0b0
    LONG = 0b1
    
    @staticmethod
    def parse(code: chr) -> SingleBitSize:
        code = code.upper()
        if code == 'W':
            return SingleBitSize.WORD
        if code == 'L':
            return SingleBitSize.LONG

class OpSize(Enum):
    """
    Represents the 3 lengths associated with operations, either Byte Word or Long word

    For example: the OpSize for MOVE.B xxx, yyy is Byte
    """
    BYTE = 1
    WORD = 2
    LONG = 4

    def __eq__(self, other):
        if isinstance(other, OpSize):
            return self.get_number_of_bytes() == other.get_number_of_bytes()
        elif isinstance(other, int):
            return self.get_number_of_bytes() == other

    def get_number_of_bytes(self) -> int:
        """
        Gets the number of bytes associated with an opsize
        :param: size - the OpSize object to get the number of bytes for
        :return:
        """
        if self is OpSize.BYTE:
            return 1
        if self is OpSize.WORD:
            return 2
        if self is OpSize.LONG:
            return 4

    @staticmethod
    def parse(code: chr) -> OpSize:
        """
        Converts the input character to the corresponding OpSize

        >>> OpSize.parse('b')
        <OpSize.BYTE: 1>

        >>> OpSize.parse('B')
        <OpSize.BYTE: 1>

        >>> OpSize.parse('W')
        <OpSize.WORD: 2>

        >>> OpSize.parse('l')
        <OpSize.LONG: 4>

        :param code:
        :return:
        """
        code = code.upper()
        if code == 'B':
            return OpSize.BYTE
        if code == 'W':
            return OpSize.WORD
        if code == 'L':
            return OpSize.LONG
