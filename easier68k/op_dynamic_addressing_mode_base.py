from abc import ABC, abstractmethod, abstractproperty
from typing import Optional
from .opcode_assembler import OpCodeAssembler
from .assembly_parameter import AssemblyParameter
from .ea_mode import EAMode
from .ea_mode_bin import EAModeBinary
from .op_size import Size, OpSize
from .m68k import M68K
from .register import Register
from .memory_value import MemoryValue
from .assembly_transformer import Literal
from .opcode_base import OpCodeBase

class DynamicAddressingModeOpCodeBase(OpCodeBase):
    """
    Base class which implements getting the addressing mode and register (if applicable).

    This assumes that the last two assembly parameters are M (mode) and Xn (register).
    """
    def __init__(self):
        self.ea_mode = None
        self.register = None

    @abstractmethod
    def to_asm_values(self) -> list:
        # we can return the last two values from this list
        mode, register = self.ea_mode.get_bin_values()
        return [mode, register or self.register]

    @abstractmethod
    def from_asm_values(self, values: list):
        # subclasses of this should implement handling the rest of the values
        # this class will assume that the only relvant ones here are the last two
        mode, register = values[-2:]

        self.ea_mode = EAMode.from_bin_mode(mode, register)
        self.register = register

    def __get_address(self, size: Size, cpu: M68K) -> MemoryValue:
        """
        Gets the address register to use for 
        ARI, ARIPI, ARIPD
        """
        if self.ea_mode in [
            EAMode.ARI,
            EAMode.ARIPI,
            EAMode.ARIPD,
        ]:
            # handle ARI
            address_register = Register.get_addr_register(self.register)

            # lint: see if I can re-use this code
            if self.ea_mode == EAMode.ARI:
                address = cpu.get_register(address_register)
            elif self.ea_mode == EAMode.ARIPI:
                address = cpu.get_register(address_register)
                # increment the register
                new_address = MemoryValue(len= OpSize.WORD, unsigned_int= OpSize.WORD.value + address.get_value_unsigned())
                cpu.set_register(address_register, new_address)
            elif self.ea_mode == EAMode.ARIPD:
                old_address = cpu.get_register(address_register)
                # increment the reigster
                address = MemoryValue(len= OpSize.WORD, unsigned_int= OpSize.WORD.value + old_address.get_value_unsigned())
                cpu.set_register(address_register, address)
            return address
        else:
            return None

    def _get_IMM_address(self, size: Size, cpu: M68K) -> MemoryValue:
        """
        gets the memory value of the address of the IMM data. makes it easier to get IMM data/address
        """
        address = cpu.get_register(Register.PC).get_value_unsigned() + OpSize.WORD.value
        return MemoryValue(size, unsigned_int=address)

    def _set_ea_mode_value(self, size: Size, cpu: M68K, value: MemoryValue):
        """
        uses the ea_mode and register to set a new value
        """

        # see page 4-6
        # only memory alterable ea_modes are used here
        # cannot use drd

        assert self.ea_mode != EAMode.IMM, "This doesn't make sense?"
        assert self.ea_mode not in [
            EAMode.DRD, EAMode.ARD
        ], "These are not valid modes for setting the value"

        if self.ea_mode in [
            EAMode.ARI,
            EAMode.ARIPI,
            EAMode.ARIPD,
        ]:
            # get the address
            adr = self.__get_address(size, cpu)
            cpu.memory.set(self.size, adr.get_value_unsigned(), value)

        if self.ea_mode == EAMode.ALA or self.ea_mode == EAMode.AWA:
            # get the address following the PC
            # set the value at that address
            imm_size = OpSize.WORD if self.ea_mode == EAMode.AWA else OpSize.LONG
            addr = self._get_IMM_address(OpSize.WORD, cpu).get_value_unsigned()
            print(f"addr {addr:x} value {value}")
            # cpu.memory.set(self.size, addr, value)
            addr = cpu.memory.get(OpSize.WORD, addr).get_value_unsigned()
            cpu.memory.set(imm_size, addr, value)

    def _get_ea_mode_value(self, size: OpSize, cpu: M68K) -> MemoryValue:
        """
        Uses the ea_mode and register to get the value specified.
        TODO should also create one to set the value
        """
        if self.ea_mode == EAMode.IMM:
            # get value at PC + 2 (word)
            imm_location = cpu.get_register(Register.PC).get_value_unsigned() + OpSize.WORD.value
            return cpu.memory.get(self.size, imm_location)

        if self.ea_mode == EAMode.DRD:
            # Direct, so look up the location from the register
            # then return the value at that location            
            # TODO move this to the class so this doesn't have to be instantiated each time
            data_register = Register.get_data_register(self.register)
            return cpu.get_register(data_register)

        if self.ea_mode in [EAMode.ARIPI, EAMode.ARIPD, EAMode.ARI]:
            address_register = Register.get_addr_register(self.register)

            if self.ea_mode == EAMode.ARI:
                address = cpu.get_register(address_register)
            elif self.ea_mode == EAMode.ARIPI:
                address = cpu.get_register(address_register)
                # increment the register
                new_address = MemoryValue(len= OpSize.WORD, unsigned_int= OpSize.WORD.value + address.get_value_unsigned())
                cpu.set_register(address_register, new_address)
            elif self.ea_mode == EAMode.ARIPD:
                old_address = cpu.get_register(address_register)
                # decrement the reigster
                address = MemoryValue(len= OpSize.WORD, unsigned_int=old_address.get_value_unsigned() - OpSize.WORD.value)
                cpu.set_register(address_register, address)

            return cpu.memory.get(self.size, address.get_value_unsigned())
        
        if self.ea_mode in [EAMode.ALA, EAMode.AWA]:
            # TODO handle distinction between long and word here
            imm_location = cpu.get_register(Register.PC).get_value_unsigned() + OpSize.WORD.value
            address = MemoryValue(self.size, unsigned_int=imm_location)
            location = cpu.memory.get(self.size, address).get_value_unsigned()
            return cpu.memory.get(self.size, location)
        