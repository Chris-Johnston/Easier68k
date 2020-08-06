import pytest
from easier68k import *

tree = BinaryPrefixTree(assemblers)

@pytest.mark.parametrize("binary,expected_type",
[
    (0b0100_1110_0111_0010, StopAssembler),
    (0b0100_1110_0111_0001, NopAssembler),
    (0b0100_1110_0111_0000, ResetAssembler),
    (0b0000_1000_0000_0000, BtstAssembler),
    (0b0100_1110_0111_0011, RteAssembler),
    (0b0100_1110_0111_0101, RtsAssembler),
    (0b0100_1110_0111_0110, TrapvAssembler),
    (0b0100_1110_0111_0111, RtrAssembler),
    (0b0100_1010_1111_1100, IllegalAssembler),
    (0b1101_0000_0000_0000, AddAssembler),
    (0b0000_0000_0000_0000, OriAssembler),
    (0b0000_0010_0000_0000, AndiAssembler),
    (0b0000_0100_0000_0000, SubiAssembler),
    (0b0000_0110_0000_0000, AddiAssembler),
    (0b0000_1100_0000_0000, EoriAssembler),
    (0b0100_0000_0000_0000, NegxAssembler),
    (0b0100_0010_0000_0000, ClrAssembler),
    (0b0100_0100_0000_0000, NegAssembler),
    (0b0100_0110_0000_0000, NotAssembler),
    (0b0100_1010_0000_0000, TstAssembler),
    (0b0000_0000_0000_0000, MoveAssembler),
    (0b1111_0000_0000_0000, None),
    (0b0111_0000_0000_0000, None),
])
def test_assembler_tree(binary, expected_type):
    assembler = tree.get_assembler(binary)
    if expected_type is None:
        assert assembler is None
    else:
        assert assembler is not None
        assert isinstance(assembler, expected_type)
        assert assembler.is_match(binary)
        values = assembler.disassemble_values(binary)
        assert values is not None
        out_word = assembler.assemble(values)
        assert out_word is not None
        assert binary == out_word
