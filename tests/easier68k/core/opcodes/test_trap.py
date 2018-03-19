from easier68k.core.opcodes.trap import Trap
from easier68k.core.models.trap_vector import TrapVector

def test_disassemble_instruction():
    val = 0b0100111001001010.to_bytes(2, byteorder='big', signed=False)

    a = Trap.disassemble_instruction(val)
    assert a.task.get_value() == 0b1010


def test_trap_assemble():
    val = 0b0100111001001111.to_bytes(2, byteorder='big', signed=False)

    a = Trap(TrapVector(15))

    assert val == a.assemble()