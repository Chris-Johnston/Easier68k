"""
Tests for the assembly parameter
"""

import pytest

from easier68k.core.models.assembly_parameter import AssemblyParameter
from easier68k.core.enum.ea_mode import EAMode

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

    with pytest.raises(AssertionError):
        # values must be unsigned
        AssemblyParameter(EAMode.IMM, -1)

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
