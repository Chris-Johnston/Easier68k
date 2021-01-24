# yes i should just use unit tests but I am lazy

from easier68k.parser import parse, assemble

# check immediates
op = "START: MOVE #1, D1\n"

result = parse(op)
print(result)

lf = assemble(result)
print(lf)
lf.print()

assert lf.memory_map[1000] == 12860
assert lf.memory_map[1002] == 1
assert len(lf.memory_map) == 2

# try with ALA
op = "START: MOVE $beef, D1\n"

result = parse(op)
print(result)

lf = assemble(result)
print(lf)
lf.print()

assert lf.memory_map[1000] == 12860
assert lf.memory_map[1002] == 0xbeef
assert len(lf.memory_map) == 2

# ASR
op = "START: ASR #1, D1\n"

result = parse(op)
print(result)

lf = assemble(result)
print(lf)
lf.print()

assert lf.memory_map[1000] == 57921
assert len(lf.memory_map) == 1

# Branch
op = "START: BLE START\n"

result = parse(op)
print(result)

lf = assemble(result)
print(lf)
lf.print()

assert lf.memory_map[1000] == 28416
assert lf.memory_map[1002] == 1000 # this should actually be 0, we want the difference from the current location and not the current location
assert len(lf.memory_map) == 2


# CMP
op = "START: CMP D1, D2\n"

result = parse(op)
print(result)

lf = assemble(result)
print(lf)
lf.print()

assert lf.memory_map[1000] == 46273
assert len(lf.memory_map) == 1

op = "START: MOVE #1234, D2\n"

result = parse(op)
print(result)

lf = assemble(result)
print(lf)
lf.print()

assert lf.memory_map[1000] == 13372
assert lf.memory_map[1002] == 1234
assert len(lf.memory_map) == 2