import pytest

from easier68k.simulator.memory import Memory, UnalignedMemoryAccessError, OutOfBoundsMemoryError
from easier68k.core.models.memory_value import MemoryValue
from easier68k.core.enum.op_size import OpSize

def test_memory_set_get():
    memory = Memory()

    # should start all zeroed out
    # also test get returns appropriate sizes
    a = MemoryValue(OpSize.LONG)
    a.set_value_bytes(b'\x00\x00\x00\x00')

    assert memory.get(OpSize.LONG, 0x00).get_value_bytes() == b'\x00\x00\x00\x00'
    assert memory.get(OpSize.WORD, 0x100000).get_value_bytes() == b'\x00\x00'
    assert memory.get(OpSize.BYTE, 0xFFFFFF).get_value_bytes() == b'\x00'

    mv = MemoryValue(OpSize.BYTE)
    mv.set_value_bytes(b'\xFF')

    # some basic set tests
    memory.set(OpSize.BYTE, 0x00, mv)
    assert memory.get(OpSize.BYTE, 0x00).get_value_bytes() == b'\xFF'
    assert memory.get(OpSize.WORD, 0x00).get_value_bytes() == b'\xFF\x00'
    assert memory.get(OpSize.LONG, 0x00).get_value_bytes() == b'\xFF\x00\x00\x00'

    mv = MemoryValue(OpSize.BYTE)
    mv.set_value_bytes(b'\xBE')
    memory.set(OpSize.BYTE, 0x000002, mv)

    mv = MemoryValue(OpSize.BYTE)
    mv.set_value_bytes(b'\xEF')
    memory.set(OpSize.BYTE, 0x000003, mv)

    assert memory.get(OpSize.LONG, 0x00).get_value_bytes() == b'\xFF\x00\xBE\xEF'

    mv = MemoryValue(OpSize.WORD)
    mv.set_value_bytes(b'\x01\x23')
    memory.set(OpSize.WORD, 0x001000, mv)

    assert memory.get(OpSize.LONG, 0x001000).get_value_bytes() == b'\x01\x23\x00\x00'

    mv = MemoryValue(OpSize.LONG)
    mv.set_value_bytes(b'\x45\x67\x89\xAB')
    memory.set(OpSize.LONG, 0x100000, mv)

    assert memory.get(OpSize.LONG, 0x100000).get_value_bytes() == b'\x45\x67\x89\xAB'


    # test some error handling
    with pytest.raises(UnalignedMemoryAccessError):
        memory.get(OpSize.WORD, 0x000001)
    with pytest.raises(UnalignedMemoryAccessError):
        memory.set(OpSize.LONG, 0x000001, MemoryValue(OpSize.WORD, bytes=b'\xDE\xAD'))

    with pytest.raises(OutOfBoundsMemoryError):
        memory.get(OpSize.LONG, 0xFFFFFF4)
    with pytest.raises(OutOfBoundsMemoryError):
        memory.get(OpSize.WORD, 0xFFFFFF2)

    with pytest.raises(OutOfBoundsMemoryError):
        memory.get(OpSize.BYTE, -1)

    # no exception here
    memory.get(OpSize.BYTE, 0xFFFFFF)
    memory.get(OpSize.WORD, 0xFFFFFE)
    memory.get(OpSize.LONG, 0xFFFFFC)


def test_memory_save_load(tmpdir):
    # test saving and loading
    memory = Memory()
    path = tmpdir.join('memoryDump.raw').strpath

    var = MemoryValue(OpSize.LONG)
    var.set_value_unsigned_int(0xFF00BEEF)

    memory.set(OpSize.LONG, 0x00, var)
    var.set_value_unsigned_int(0x01230000)
    memory.set(OpSize.LONG, 0x001000, var)
    var.set_value_unsigned_int(0x456789AB)
    memory.set(OpSize.LONG, 0x100000, var)

    memory.save_memory(open(path, 'wb'))


    load_test = Memory()
    load_test.load_memory(open(path, 'rb'))

    assert load_test.get(OpSize.LONG, 0x00).get_value_unsigned() == 0xFF00BEEF
    assert load_test.get(OpSize.LONG, 0x001000).get_value_unsigned() == 0x01230000
    assert load_test.get(OpSize.LONG, 0x100000).get_value_unsigned() == 0x456789AB
