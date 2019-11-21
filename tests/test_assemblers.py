from easier68k import (
    assemblers,
    BinaryPrefixTree,
    ResetAssembler,
    NopAssembler,
    StopAssembler
)

tree = BinaryPrefixTree(assemblers)

test_map = {
    0b0100_1110_0111_0010: StopAssembler,
    0b0100_1110_0111_0001: NopAssembler,
    0b0100_1110_0111_0000: ResetAssembler,
    0b0000_1000_0000_0000: BtstAssembler,
    0b1111_0000_0000_0000: None,
    0b0111_0000_0000_0000: None,
}

def test_assembler_tree():
    for binary in test_map:
        expected_type = test_map[binary]
        assembler = tree.get_assembler(expected_type)
        if expected_type is None:
            assert assembler is None
        else:
            assert isinstance(assembler, expected_type)
            assert assembler.is_match(binary)
            values = sassembler.disassemble_values(binary)
            assert values is not None
            out_word = assembler.assembe(values)
            assert out_word is not None
            assert binary == out_word
