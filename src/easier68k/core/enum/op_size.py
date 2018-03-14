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

from enum import IntEnum

# forward declaration so that types can return correctly
class MoveSize(IntEnum):
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