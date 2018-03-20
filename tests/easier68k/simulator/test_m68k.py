import pytest

from easier68k.simulator.m68k import M68K
from easier68k.core.enum.register import Register, MEMORY_LIMITED_ADDRESS_REGISTERS, DATA_REGISTERS
from easier68k.core.models.list_file import ListFile
from easier68k.simulator.memory import Memory

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
    assert a.get_register_value(reg) == 0

    # try setting w/o errors
    a.set_register_value(reg, 0x3200)

    # ensure that this value can be retrieved without error
    assert a.get_register_value(reg) == 0x3200

    # test of invalid input
    with pytest.raises(AssertionError):
        a.set_register_value(reg, -1)

    a.set_register_value(reg, 16777216)

    with pytest.raises(AssertionError):
        # 1 beyond the max value
        a.set_register_value(reg, 16777216 + 1)

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
    assert sim.get_register_value(reg) == 0
    # now try setting a single byte value to the register
    sim.set_register_value(reg, 0xAF)
    # ensure the values are accurate
    assert sim.get_register_value(reg) == 0xAF

    sim.set_register_value(reg, 0xFF)
    assert sim.get_register_value(reg) == 0xFF

    # hasn't died yet (hopefully)
    # so move on to 2 bytes
    sim.set_register_value(reg, 0xBEEF)
    assert sim.get_register_value(reg) == 0xBEEF
    sim.set_register_value(reg, 0xFFFF)
    assert sim.get_register_value(reg) == 0xFFFF

    # 3
    sim.set_register_value(reg, 0xBEEFFE)
    assert sim.get_register_value(reg) == 0xBEEFFE
    sim.set_register_value(reg, 0xFFFFFF)
    assert sim.get_register_value(reg) == 0xFFFFFF

    # set all 4 bytes including max value
    sim.set_register_value(reg, 0xDEADBEEF)
    assert sim.get_register_value(reg) == 0xDEADBEEF
    sim.set_register_value(reg, 0xFFFFFFFF)
    assert sim.get_register_value(reg) == 0xFFFFFFFF

    # mess with out of bounds setting
    with pytest.raises(AssertionError):
        sim.set_register_value(reg, -1)

    with pytest.raises(AssertionError):
        sim.set_register_value(reg, 0xFFFFFFFF + 1)

    # ensure that the resulting value is still accurate after errors
    assert sim.get_register_value(reg) == 0xFFFFFFFF


def test_condition_code_register():
    """
    Test the special case condition code register which is only a single byte
    Also check that the status bits are set and read properly
    :return:
    """

    # the condition code register is a single byte so it cannot be tested like the other
    # registers
    a = M68K()

    # test initial value
    assert a.get_register_value(Register.ConditionCodeRegister) == 0
    assert a.get_register_value(Register.CCR) == 0

    # test setting a value in bounds
    a.set_register_value(Register.CCR, 0xAF)

    # after this can assume that the enums are correctly equal to each other
    assert a.get_register_value(Register.ConditionCodeRegister) == 0xAF
    assert a.get_register_value(Register.CCR) == 0xAF

    # now test invalid input
    with pytest.raises(AssertionError):
        a.set_register_value(Register.CCR, -1)
    with pytest.raises(AssertionError):
        a.set_register_value(Register.CCR, 0xFF + 1)

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
    assert(m68k.memory.get(Memory.Word, 0x00aaaaaa) == bytearray.fromhex('0000'))
    m68k.step_instruction()
    assert(m68k.get_program_counter_value() == 1032)
    assert(m68k.memory.get(Memory.Word, 0x00aaaaaa) == bytearray.fromhex('abcd'))
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


