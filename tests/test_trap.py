from easier68k.opcodes import Trap
from easier68k import TrapVector
from easier68k import M68K
from easier68k import Register
from easier68k import TrapTask
from easier68k import TrapVectors
from easier68k import MemoryValue
from easier68k import OpSize

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
    sim.memory.set(4, 0x1000, MemoryValue(OpSize.LONG, bytes=bytearray([0x41, 0x42, 0x43, 0x00])))

    sim.set_register(Register.A1, MemoryValue(OpSize.WORD, unsigned_int=0x1000))
    sim.set_register(Register.D0, MemoryValue(OpSize.WORD, unsigned_int=TrapTask.DisplayNullTermString))

    exec = Trap(TrapVectors.IO)

    exec.execute(sim)

    # check that the previous command returned this
    captured = capsys.readouterr()
    assert captured.out == 'ABC'


def test_display_test_increment_pc(capsys):

    sim = M68K()

    # null term string ABC\0
    sim.memory.set(4, 0x1000, MemoryValue(OpSize.LONG, bytes=bytearray([0x41, 0x42, 0x43, 0x00])))

    sim.set_register(Register.A1, MemoryValue(OpSize.WORD, unsigned_int=0x1000))
    sim.set_register(Register.D0, MemoryValue(OpSize.WORD, unsigned_int=TrapTask.DisplayNullTermString))

    exec = Trap(TrapVectors.IO)

    sim.set_program_counter_value(0x1000)

    exec.execute(sim)

    assert sim.get_program_counter_value() == 0x1000 + 2

    # check that the previous command returned this
    captured = capsys.readouterr()
    assert captured.out == 'ABC'


def test_display_null_term_string_crlf(capsys):

    sim = M68K()

    # null term string ABC\0
    sim.memory.set(OpSize.LONG, 0x1000, MemoryValue(OpSize.LONG, bytes=bytearray([0x41, 0x42, 0x43, 0x00])))

    sim.set_register(Register.A1, MemoryValue(OpSize.WORD, unsigned_int=0x1000))
    sim.set_register(Register.D0, MemoryValue(OpSize.WORD, unsigned_int=TrapTask.DisplayNullTermStringWithCRLF))

    exec = Trap(TrapVectors.IO)

    exec.execute(sim)

    # check that the previous command returned this
    captured = capsys.readouterr()
    assert captured.out == 'ABC\n'

def test_display_signed_number(capsys):
    sim = M68K()

    sim.set_register(Register.D1, MemoryValue(OpSize.WORD, signed_int=123))
    sim.set_register(Register.D0, MemoryValue(OpSize.WORD, unsigned_int=TrapTask.DisplaySignedNumber))

    exec = Trap(TrapVectors.IO)

    exec.execute(sim)

    # check that the previous command returned this
    captured = capsys.readouterr()
    assert captured.out == '123'

def test_display_signed_number_negative(capsys):
    sim = M68K()

    sim.set_register(Register.D1, MemoryValue(OpSize.BYTE, signed_int=-123))
    sim.set_register(Register.D0, MemoryValue(OpSize.WORD, unsigned_int=TrapTask.DisplaySignedNumber))

    exec = Trap(TrapVectors.IO)

    exec.execute(sim)

    # check that the previous command returned this
    captured = capsys.readouterr()
    assert captured.out == '-123'


def test_display_single_character(capsys):
    sim = M68K()

    sim.set_register(Register.D1, MemoryValue(OpSize.WORD, unsigned_int=ord('a')))
    sim.set_register(Register.D0, MemoryValue(OpSize.WORD, unsigned_int=TrapTask.DisplaySingleCharacter))

    exec = Trap(TrapVectors.IO)

    exec.execute(sim)

    # check that the previous command returned this
    captured = capsys.readouterr()
    assert captured.out == 'a'


def test_read_null_term_string(capsys):
    sim = M68K()

    sim.set_register(Register.A1, MemoryValue(OpSize.WORD, unsigned_int=0x1000))
    sim.set_register(Register.D0, MemoryValue(OpSize.WORD, unsigned_int=TrapTask.DisplaySingleCharacter))

    exec = Trap(TrapVectors.IO)
    exec.use_debug_input = True
    exec.debug_input = 'test123!'
