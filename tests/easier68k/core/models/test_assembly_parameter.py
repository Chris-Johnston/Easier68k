"""
Tests for the assembly parameter
"""

import pytest

from easier68k.core.models.assembly_parameter import AssemblyParameter
from easier68k.core.enum.ea_mode import EAMode
from easier68k.simulator.m68k import M68K
from easier68k.core.enum.register import Register, FULL_SIZE_REGISTERS, MEMORY_LIMITED_ADDRESS_REGISTERS
from easier68k.core.models.memory_value import MemoryValue
from easier68k.core.enum.op_size import OpSize

# should try to make this a constant only defined once
MAX_MEMORY_LOCATION = 16777216  # 2^24


def test_assembly_parameter():
    """
    Tests for the assembly parameter class
    :return:
    """

    # check valid IMM cstr

    ap = AssemblyParameter(EAMode.IMM, 0)
    ap = AssemblyParameter(EAMode.IMM, 0xFFFF)
    ap = AssemblyParameter(EAMode.IMM, 0xFFFFFFFF)

    # values can be negative
    AssemblyParameter(EAMode.IMM, -1)

    with pytest.raises(AssertionError):
        # values must fit in 32 bit value
        AssemblyParameter(EAMode.IMM, -2147483648 -1)

    with pytest.raises(AssertionError):
        # values must fit in 0xFFFFFFFF
        AssemblyParameter(EAMode.IMM, 0xFFFFFFFF + 1)

    # test absolute word address
    ap = AssemblyParameter(EAMode.AbsoluteWordAddress, 0)
    ap = AssemblyParameter(EAMode.AbsoluteWordAddress, 0xFFFF)
    ap = AssemblyParameter(EAMode.AbsoluteWordAddress, MAX_MEMORY_LOCATION)

    with pytest.raises(AssertionError):
        # unsigned values
        AssemblyParameter(EAMode.AbsoluteWordAddress, -1)

    with pytest.raises(AssertionError):
        # unsigned values
        AssemblyParameter(EAMode.AbsoluteWordAddress, MAX_MEMORY_LOCATION + 1)

    # test absolute long address
    ap = AssemblyParameter(EAMode.AbsoluteLongAddress, 0)
    ap = AssemblyParameter(EAMode.AbsoluteLongAddress, 0xFFFF)
    ap = AssemblyParameter(EAMode.AbsoluteLongAddress, MAX_MEMORY_LOCATION)

    with pytest.raises(AssertionError):
        # unsigned values
        AssemblyParameter(EAMode.AbsoluteLongAddress, -1)

    with pytest.raises(AssertionError):
        # unsigned values
        AssemblyParameter(EAMode.AbsoluteLongAddress, MAX_MEMORY_LOCATION + 1)

    # test all of the register modes
    register_modes = [EAMode.DataRegisterDirect, EAMode.AddressRegisterIndirectPreDecrement,
                      EAMode.AddressRegisterIndirect, EAMode.AddressRegisterIndirectPostIncrement,
                      EAMode.AddressRegisterDirect]

    for mode in register_modes:
        # test that all 7 can be made
        for x in range(7):
            ap = AssemblyParameter(mode, x)

        with pytest.raises(AssertionError):
            AssemblyParameter(mode, -1)

        with pytest.raises(AssertionError):
            AssemblyParameter(mode, 8)


def test_get_value():
    """
    Test the behavior of AssemblyParameter get value
    :return:
    """
    sim = M68K()

    # set up the memory
    for x in range(0x1000, 0x2000, 4):
        v = MemoryValue(OpSize.LONG)
        v.set_value_signed_int(2 * x)
        sim.memory.set(OpSize.LONG, x, v)
        assert sim.memory.get(OpSize.LONG, x).get_value_unsigned() == 2 * x

    # test immediate

    # ensure that get value works correctly for almost all values of assembly parameter immediate
    # have it skip every 0xFF because it takes long enough already
    for x in [0, 0xFF, 0xFFFF, 0xFFFFF, 0xFFFFFF, 0xFFFFFFFF]:
        ap = AssemblyParameter(EAMode.IMM, x)
        assert ap.get_value(sim, OpSize.LONG).get_value_unsigned() == x

    # test address register direct
    for x in [0, 0xFFFF, 0xFFFFF, MAX_MEMORY_LOCATION]:
        for r in range(7):
            reg_val = MemoryValue(OpSize.LONG)
            reg_val.set_value_unsigned_int(x)

            # set the register value to a memory location
            sim.set_register(Register(r + Register.A0), reg_val)
            # ensure it set proper
            assert sim.get_register(Register(r + Register.A0)).get_value_unsigned() == x

            # now set the param to get the value of an address register
            ap = AssemblyParameter(EAMode.AddressRegisterDirect, r)
            assert ap.get_value(sim).get_value_unsigned() == x

    val = MemoryValue(OpSize.WORD)

    # test address register indirect
    for x in range(0x1000, 0x2000, 4):
        for r in [Register.A0, Register.A1, Register.A2, Register.A3, Register.A4,
                  Register.A5, Register.A6, Register.A7]:
            val.set_value_unsigned_int(x)

            sim.set_register(r, val)
            # set the register value to a memory location
            # ensure it set
            assert sim.get_register(r).get_value_unsigned() == x

            # now set up the parameter to get the value that the address reg points to
            ap = AssemblyParameter(EAMode.AddressRegisterIndirect, (r.value - Register.A0.value))
            # ensure that the value matches
            assert ap.get_value(sim, OpSize.LONG).get_value_unsigned() == (2 * x)

    # test that address register indirect post increment and pre decrement
    # work properly

    sim.set_register(Register.A0, MemoryValue(OpSize.WORD, unsigned_int=0x1000))

    ap = AssemblyParameter(EAMode.AddressRegisterIndirectPostIncrement, 0)
    v = ap.get_value(sim)

    assert v.get_value_unsigned() == 2 * 0x1000

    assert sim.get_register(Register.A0).get_value_unsigned() == 0x1000 + 4

    # pre decrement

    ap = AssemblyParameter(EAMode.AddressRegisterIndirectPreDecrement, 0)
    assert ap.get_value(sim).get_value_unsigned() == 2 * 0x1000

    assert sim.get_register(Register.A0).get_value_unsigned() == 0x1000
    # test absolute long / word address
    ap = AssemblyParameter(EAMode.AbsoluteWordAddress, 0x1000)
    assert ap.get_value(sim).get_value_unsigned() == 0x1000

    ap = AssemblyParameter(EAMode.AbsoluteLongAddress, 0x1000)
    assert ap.get_value(sim).get_value_unsigned() == 0x1000


def test_assembly_parameter_set_value():
    """
    Tests to see that assembly_parameter set_value works properly
    :return:
    """

    sim = M68K()

    ap = AssemblyParameter(EAMode.IMM, 123)

    mv = MemoryValue(OpSize.WORD)
    mv.set_value_unsigned_int(1234)

    # immediate set should throw assertion error
    with pytest.raises(AssertionError):
        ap.set_value(sim, mv)

    # test data register set

    ap = AssemblyParameter(EAMode.DataRegisterDirect, 3)

    mv.set_value_unsigned_int(123)
    ap.set_value(sim, mv)

    assert sim.get_register(Register.D3) == 123

    # test address register direct

    ap = AssemblyParameter(EAMode.AddressRegisterDirect, 5)

    mv.set_value_unsigned_int(0x120)
    ap.set_value(sim, mv)

    assert sim.get_register(Register.A5) == 0x120

    val = MemoryValue(OpSize.LONG)
    val.set_value_unsigned_int(0x1ABBAABB)

    # set some memory at 0x123
    sim.memory.set(OpSize.LONG, 0x120, val)

    # ensure set proper
    assert sim.memory.get(OpSize.LONG, 0x120) == 0x1ABBAABB

    # now test address register indirect
    ap = AssemblyParameter(EAMode.AddressRegisterIndirect, 5)

    mv = MemoryValue(OpSize.LONG)
    mv.set_value_unsigned_int(0x123123)
    # set the value
    ap.set_value(sim, mv)

    # ensure that it changed
    assert sim.memory.get(OpSize.LONG, 0x120).get_value_unsigned() == 0x123123

    # test address register indirect pre and post

    ap = AssemblyParameter(EAMode.AddressRegisterIndirectPostIncrement, 5)
    ap.set_value(sim, MemoryValue(OpSize.WORD, unsigned_int=0xAA))

    assert sim.memory.get(OpSize.WORD, 0x120).get_value_unsigned() == 0xAA

    ap = AssemblyParameter(EAMode.AddressRegisterIndirectPreDecrement, 5)
    ap.set_value(sim, MemoryValue(OpSize.WORD, unsigned_int=0xBB))

    assert sim.memory.get(OpSize.WORD, 0x120).get_value_unsigned() == 0xBB

    # test absolute addresses

    mv.set_value_unsigned_int(0xCC)

    ap = AssemblyParameter(EAMode.AbsoluteWordAddress, 0x120)
    ap.set_value(sim, mv)

    assert sim.memory.get(OpSize.LONG, 0x120).get_value_unsigned() == 0xCC

    mv.set_value_unsigned_int(0xDD)

    ap = AssemblyParameter(EAMode.AbsoluteLongAddress, 0x120)
    ap.set_value(sim, mv)

    assert sim.memory.get(OpSize.LONG, 0x120).get_value_unsigned() == 0xDD
