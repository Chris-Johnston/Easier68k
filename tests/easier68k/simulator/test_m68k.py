import pytest

from easier68k.simulator.m68k import M68K
from easier68k.core.enum.register import Register, MEMORY_LIMITED_ADDRESS_REGISTERS, DATA_REGISTERS
from easier68k.core.models.list_file import ListFile
from easier68k.simulator.memory import Memory
from easier68k.core.models.memory_value import MemoryValue
from easier68k.core.enum.op_size import OpSize

def test_address_registers():
    """
    Test the other registers to ensure that they can read and write properly
    :return:
    """

    a = M68K()

    # test all of the 4 byte registers (32 bit)
    # exclude the program counter due to its restrictions
    normal_registers = MEMORY_LIMITED_ADDRESS_REGISTERS
    for reg in normal_registers:
        _test_single_address_register(a, reg)


def test_program_counter():
    """
    Do the test single address register tests with the program counter interface
    :return:
    """
    a = M68K()

    # ensure that its value defaults to zero
    assert a.get_program_counter_value() == 0

    # try setting w/o errors
    a.set_program_counter_value(0x3200)

    # ensure that this value can be retrieved without error
    assert a.get_program_counter_value() == 0x3200

    # test of invalid input
    with pytest.raises(AssertionError):
        a.set_program_counter_value(-1)

    a.set_program_counter_value(16777216)

    with pytest.raises(AssertionError):
        # 1 beyond the max value
        a.set_program_counter_value(16777216 + 1)


def _test_single_address_register(a :M68K, reg: Register):
    """
    Tests for the address registers that are limited by the size of memory
    :return:
    """

    # ensure that its value defaults to zero
    assert a.get_register(reg) == 0

    # try setting w/o errors
    a.set_register(reg, MemoryValue(OpSize.WORD, unsigned_int=0x3200))

    # ensure that this value can be retrieved without error
    assert a.get_register(reg) == 0x3200

    # set the max size without error
    a.set_register(reg, MemoryValue(OpSize.LONG, unsigned_int=16777216))

def test_data_registers():
    """
    Test the other registers to ensure that they can read and write properly
    :return:
    """

    a = M68K()

    # test all of the 4 byte DATA registers that can have any value without issues
    normal_registers = DATA_REGISTERS
    for reg in normal_registers:
        _test_single_data_register(a, reg)


def _test_single_data_register(sim: M68K, reg: Register):
    """
    Tests a single register
    :param sim:
    :param reg:
    :return:
    """

    # test that the initial value is zero
    assert sim.get_register(reg) == 0
    # now try setting a single byte value to the register
    mv = MemoryValue(OpSize.BYTE)
    mv.set_value_unsigned_int(0xAF)
    sim.set_register(reg, mv)
    # ensure the values are accurate
    assert sim.get_register(reg).get_value_unsigned() == 0xAF

    mv = MemoryValue(OpSize.BYTE)
    mv.set_value_unsigned_int(0xFF)
    sim.set_register(reg, mv)

    assert sim.get_register(reg).get_value_unsigned() == 0xFF

    # hasn't died yet (hopefully)
    # so move on to 2 bytes
    mv = MemoryValue(OpSize.WORD, unsigned_int=0xBEEF)
    sim.set_register(reg, mv)
    assert sim.get_register(reg).get_value_unsigned() == 0xBEEF
    mv = MemoryValue(OpSize.WORD, unsigned_int=0xFFFF)
    sim.set_register(reg, mv)
    assert sim.get_register(reg).get_value_unsigned() == 0xFFFF

    # 3
    mv = MemoryValue(OpSize.LONG, unsigned_int=0x00BEEFFE)
    sim.set_register(reg, mv)
    assert sim.get_register(reg) == 0xBEEFFE
    mv = MemoryValue(OpSize.LONG, unsigned_int=0x00FFFFFF)
    sim.set_register(reg, mv)
    assert sim.get_register(reg) == 0xFFFFFF

    # set all 4 bytes including max value
    mv = MemoryValue(OpSize.LONG, unsigned_int=0xDEADBEEF)
    sim.set_register(reg, mv)
    assert sim.get_register(reg).get_value_unsigned() == 0xDEADBEEF
    mv = MemoryValue(OpSize.LONG, unsigned_int=0xFFFFFFFF)
    sim.set_register(reg, mv)
    assert sim.get_register(reg).get_value_unsigned() == 0xFFFFFFFF

    # should not check for out of range setting, because
    # this is handled byy MemoryValue already

def test_condition_code_register():
    """
    Test the special case condition code register which is only a single byte
    Also check that the status bits are set and read properly
    :return:
    """

    # the condition code register is a single byte so it cannot be tested like the other
    # registers
    a = M68K()

    assert a.get_register(Register.CCR) == 0
    assert a.get_register(Register.ConditionCodeRegister) == 0

    val = MemoryValue(OpSize.BYTE)
    val.set_value_unsigned_int(0xAF)

    a.set_register(Register.ConditionCodeRegister, val)

    # after this can assume that the enums are correctly equal to each other
    assert a.get_register(Register.ConditionCodeRegister).get_value_unsigned() == 0xAF
    assert a.get_register(Register.CCR).get_value_unsigned() == 0xAF

def test_full_integration():
    m68k = M68K()

    list_file = ListFile()

    '''
    ORG 1036
MAGIC:
    DC.W $ABCD
    ORG    1024
START:
    MOVE.W #$ABCD, ($00AAAAAA).L
    SIMHALT
    END    START 
    '''

    # essentiall contains 'Move.W #$abcd,($00aaaaaa).L'
    list_file.load_from_json("""
{
    "data": {
        "1024": "33fcabcd00aaaaaa",
        "1032": "ffffffff",
        "1036": "abcd"
    },
    "startingExecutionAddress": 1024,
    "symbols": {
        "magic": 1036
    }
}
    """)

    m68k.load_list_file(list_file)
    assert(m68k.get_program_counter_value() == 1024)
    assert(m68k.memory.get(OpSize.WORD, 0x00aaaaaa).get_value_unsigned() == 0x0000)
    m68k.step_instruction()
    assert(m68k.get_program_counter_value() == 1032)
    assert(m68k.memory.get(OpSize.WORD, 0x00aaaaaa).get_value_unsigned() == 0xABCD)
    m68k.step_instruction()
    assert m68k.get_program_counter_value() == 1036
    assert m68k.halted

def test_auto_execute():
    m68k = M68K()

    list_file = ListFile()

    list_file.load_from_json("""
    {
        "data": {
            "1024": "33fcabcd00aaaaaa",
            "1032": "ffffffff",
            "1036": "abcd"
        },
        "startingExecutionAddress": 1024,
        "symbols": {
            "magic": 1036
        }
    }
        """)

    m68k.load_list_file(list_file)

    # run the auto execute
    m68k.clock_auto_cycle = True
    m68k.run()

    # check that the program counter stopped in the right location
    assert m68k.get_program_counter_value() == 1036

    assert m68k.halted


