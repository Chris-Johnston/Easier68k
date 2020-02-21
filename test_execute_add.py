# disassembles bytes to an add assembler
# uses it to populate an add opcode
# executes the add opcode on the CPU

# d register 1
# saved into d1
# add immediate 0b111
# add long
ADD = 0b1101_0010_1011_1100
AND = 0b1100_0010_1011_1100
SUB = 0b1001_0010_1011_1100
OR = 0b1000_0010_1011_1100

from easier68k.binary_prefix_tree import BinaryPrefixTree
from easier68k.assemblers import assemblers
from easier68k.m68k import M68K
from easier68k.register import Register

assembler_tree = BinaryPrefixTree(assemblers)

def assemble(op):
    opcode_assembler = assembler_tree.get_assembler(op)
    print(f'opcode assembler {opcode_assembler} for {op:b}')
    assert opcode_assembler is not None, f"Opcode assembler was none, not found for Op {op:b}"
    values = opcode_assembler.disassemble_values(op)
    opcode = opcode_assembler.get_opcode()
    opcode.from_asm_values(values)
    print(f'op {opcode} mode {opcode.ea_mode} register {opcode.register} dn {opcode.data_register} dir {opcode.direction} size {opcode.size}')

for op in [ADD, SUB, AND, OR]:
    assemble(op)