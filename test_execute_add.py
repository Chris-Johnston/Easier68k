# disassembles bytes to an add assembler
# uses it to populate an add opcode
# executes the add opcode on the CPU

# d register 1
# saved into d1
# add immediate 0b111
# add word
ADD = 0b1101_0010_0111_1100
AND = 0b1100_0010_1011_1100
SUB = 0b1001_0010_1011_1100
OR = 0b1000_0010_1011_1100

from easier68k.binary_prefix_tree import BinaryPrefixTree
from easier68k.assemblers import assemblers
from easier68k.m68k import M68K
from easier68k.register import Register
from easier68k.op_size import OpSize
from easier68k.memory_value import MemoryValue

print(assemblers)

assembler_tree = BinaryPrefixTree(assemblers.values())


# tests disassembling ADD SUB AND OR

def assemble(op):
    opcode_assembler = assembler_tree.get_assembler(op)
    print(f'opcode assembler {opcode_assembler} for {op:b}')
    assert opcode_assembler is not None, f"Opcode assembler was none, not found for Op {op:b}"
    values = opcode_assembler.disassemble_values(op)
    opcode = opcode_assembler.get_opcode()
    # opcode.from_asm_values(values)
    print(f'op {opcode}')

for op in [ADD, SUB, AND, OR]:
    assemble(op)

# test assembling and simulating ADD
# aka how many LOC does it take to add 2 + 2

# initialize it
op_asm = assembler_tree.get_assembler(ADD)
values = op_asm.disassemble_values(ADD)
add_op = op_asm.get_opcode()
# add_op.from_asm_values(values)

# simulate it
cpu = M68K()

# store #2 in D1
cpu.set_register(Register.D1, MemoryValue(signed_int=0x2))

# store #2 in 0x1002
cpu.memory.set(OpSize.WORD, 0x1002, MemoryValue(len = OpSize.WORD, signed_int=0x2))

# start at 0x1000
cpu.set_register(Register.PC, MemoryValue(unsigned_int=0x1000)) # 0x1000

add_op.execute(cpu)

# get the value in D1
d1_val = cpu.get_register(Register.D1)
print(f"d1 {d1_val} == 4!?")

# now do it again

ADD = 0b1101_0011_0111_1000
# $beee (0) + D1 (4) -> $beee (4)
# word

op_asm = assembler_tree.get_assembler(ADD)
values = op_asm.disassemble_values(ADD)
add_op = op_asm.get_opcode()
add_op.from_asm_values(values)

# was going to use beef but odd numbered memory, though not sure if that should be a concern
cpu.memory.set(OpSize.WORD, 0x1002, MemoryValue(len = OpSize.WORD, unsigned_int=0xbeee))

# start at 0x1000
cpu.set_register(Register.PC, MemoryValue(unsigned_int=0x1000)) # 0x1000

add_op.execute(cpu)

# check val in $beef
# beef = MemoryValue(len = OpSize.WORD, unsigned_int=0xbeef)
val = cpu.memory.get(OpSize.WORD, 0xbeee)
print(f"$beef {val} == 4")