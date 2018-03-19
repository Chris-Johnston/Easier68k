from easier68k.core.opcodes.trap import Trap
from easier68k.core.models.trap_vector import TrapVector
from easier68k.simulator.m68k import M68K
from easier68k.core.enum.register import Register
from easier68k.core.enum.trap_task import TrapTask

def test_disassemble_instruction():
    val = 0b0100111001001010.to_bytes(2, byteorder='big', signed=False)

    a = Trap.disassemble_instruction(val)
    assert a.task.get_value() == 0b1010


def test_trap_assemble():
    val = 0b0100111001001111.to_bytes(2, byteorder='big', signed=False)

    a = Trap(TrapVector(15))

    assert val == a.assemble()

def test_display_null_term_string(capsys):

    sim = M68K()

    # null term string ABC\0
    sim.memory.set(4, 0x1000, bytearray([
        0x41, 0x42, 0x43, 0x00
    ]))

    sim.set_register_value(Register.A1, 0x1000)

    exec = Trap(TrapVector(TrapTask.DisplayNullTermString.value))

    exec.execute(sim)

    # check that the previous command returned this
    captured = capsys.readouterr()
    assert captured.out == 'ABC'

def test_display_null_term_string_crlf(capsys):

    sim = M68K()

    # null term string ABC\0
    sim.memory.set(4, 0x1000, bytearray([
        0x41, 0x42, 0x43, 0x00
    ]))

    sim.set_register_value(Register.A1, 0x1000)

    exec = Trap(TrapVector(TrapTask.DisplayNullTermStringWithCRLF.value))

    exec.execute(sim)

    # check that the previous command returned this
    captured = capsys.readouterr()
    assert captured.out == 'ABC\n'
