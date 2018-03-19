from easier68k.core.opcodes.trap import Trap
from easier68k.core.models.trap_vector import TrapVector
from easier68k.simulator.m68k import M68K
from easier68k.core.enum.register import Register
from easier68k.core.enum.trap_task import TrapTask
import easier68k.core.util.input as inp
from easier68k.core.enum.trap_vector import TrapVectors

def test_disassemble_instruction():
    val = 0b0100111001001111.to_bytes(2, byteorder='big', signed=False)

    a = Trap.disassemble_instruction(val)
    assert a.trpVector == 0b1111


def test_trap_assemble():
    val = 0b0100111001001111.to_bytes(2, byteorder='big', signed=False)

    a = Trap(TrapVectors.IO)

    assert val == a.assemble()

def test_display_null_term_string(capsys):

    sim = M68K()

    # null term string ABC\0
    sim.memory.set(4, 0x1000, bytearray([
        0x41, 0x42, 0x43, 0x00
    ]))

    sim.set_register_value(Register.A1, 0x1000)
    sim.set_register_value(Register.D0, TrapTask.DisplayNullTermString)

    exec = Trap(TrapVectors.IO)

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
    sim.set_register_value(Register.D0, TrapTask.DisplayNullTermStringWithCRLF)

    exec = Trap(TrapVectors.IO)

    exec.execute(sim)

    # check that the previous command returned this
    captured = capsys.readouterr()
    assert captured.out == 'ABC\n'

def test_display_signed_number(capsys):
    sim = M68K()

    sim.set_register_value(Register.D1, 123)
    sim.set_register_value(Register.D0, TrapTask.DisplaySignedNumber)

    exec = Trap(TrapVectors.IO)

    exec.execute(sim)

    # check that the previous command returned this
    captured = capsys.readouterr()
    assert captured.out == '123'

def test_display_signed_number_negative(capsys):
    sim = M68K()

    # 2's comp of 123
    x = 123
    mask = 0xFFFFFFFF
    x = x ^ mask
    x += 1

    sim.set_register_value(Register.D1, x)
    sim.set_register_value(Register.D0, TrapTask.DisplaySignedNumber)

    exec = Trap(TrapVectors.IO)

    exec.execute(sim)

    # check that the previous command returned this
    captured = capsys.readouterr()
    assert captured.out == '-123'


def test_display_single_character(capsys):
    sim = M68K()

    sim.set_register_value(Register.D1, ord('a'))
    sim.set_register_value(Register.D0, TrapTask.DisplaySingleCharacter)

    exec = Trap(TrapVectors.IO)

    exec.execute(sim)

    # check that the previous command returned this
    captured = capsys.readouterr()
    assert captured.out == 'a'


def test_read_null_term_string(capsys):
    sim = M68K()

    sim.set_register_value(Register.A1, 0x1000)
    sim.set_register_value(Register.D0, TrapTask.ReadNullTermString)

    exec = Trap(TrapVectors.IO)
    exec.use_debug_input = True
    exec.debug_input = 'test123!'

    #with patch('easier68k.core.util.input.get_input', return_value='test123!'):
    #    exec.execute(sim)

    # exec.execute(sim)
    #
    # assert sim.memory.get(8, 0x1000) == 0