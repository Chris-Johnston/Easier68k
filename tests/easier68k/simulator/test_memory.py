import pytest

from easier68k.simulator.memory import Memory, UnalignedMemoryAccessError, OutOfBoundsMemoryError

def test_memory_set_get():
    memory = Memory()

    # should start all zeroed out
    # also test get returns appropriate sizes
    assert memory.get(Memory.Long, 0x00) == b'\x00\x00\x00\x00'
    assert memory.get(Memory.Word, 0x100000) == b'\x00\x00'
    assert memory.get(Memory.Byte, 0xFFFFFF) == b'\x00'


    # some basic set tests
    memory.set(Memory.Byte, 0x00, b'\xFF')
    assert memory.get(Memory.Byte, 0x00) == b'\xFF'
    assert memory.get(Memory.Word, 0x00) == b'\xFF\x00'
    assert memory.get(Memory.Long, 0x00) == b'\xFF\x00\x00\x00'

    memory.set(Memory.Byte, 0x000002, b'\xBE')
    memory.set(Memory.Byte, 0x000003, b'\xEF')
    assert memory.get(Memory.Long, 0x00) == b'\xFF\x00\xBE\xEF'

    memory.set(Memory.Word, 0x001000, b'\x01\x23')
    assert memory.get(Memory.Long, 0x001000) == b'\x01\x23\x00\x00'

    memory.set(Memory.Long, 0x100000, b'\x45\x67\x89\xAB')
    assert memory.get(Memory.Long, 0x100000) == b'\x45\x67\x89\xAB'


    # test some error handling
    with pytest.raises(UnalignedMemoryAccessError):
        memory.get(Memory.Word, 0x000001)
    with pytest.raises(UnalignedMemoryAccessError):
        memory.set(Memory.Long, 0x000001, b'\xDE\xAD')

    with pytest.raises(OutOfBoundsMemoryError):
        memory.get(Memory.Long, 0xFFFFFF4)
    with pytest.raises(OutOfBoundsMemoryError):
        memory.get(Memory.Word, 0xFFFFFF2)

    with pytest.raises(OutOfBoundsMemoryError):
        memory.get(Memory.Byte, -1)

    # no exception here
    memory.get(Memory.Byte, 0xFFFFFF)
    memory.get(Memory.Word, 0xFFFFFE)
    memory.get(Memory.Long, 0xFFFFFC)


def test_memory_save_load(tmpdir):
    # test saving and loading
    memory = Memory()
    path = tmpdir.join('memoryDump.raw').strpath

    memory.set(Memory.Long, 0x00, b'\xFF\x00\xBE\xEF')
    memory.set(Memory.Long, 0x001000, b'\x01\x23\x00\x00')
    memory.set(Memory.Long, 0x100000, b'\x45\x67\x89\xAB')

    memory.save_memory(open(path, 'wb'))


    load_test = Memory()
    load_test.load_memory(open(path, 'rb'))

    assert load_test.get(Memory.Long, 0x00) == b'\xFF\x00\xBE\xEF'
    assert load_test.get(Memory.Long, 0x001000) == b'\x01\x23\x00\x00'
    assert load_test.get(Memory.Long, 0x100000) == b'\x45\x67\x89\xAB'
