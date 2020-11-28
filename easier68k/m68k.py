"""
Motorola 68k chip definition
"""

from .memory import Memory
from .register import Register, FULL_SIZE_REGISTERS, ALL_ADDRESS_REGISTERS
from .condition_status_code import ConditionStatusCode
from .list_file import ListFile
import typing
import binascii
from .memory_value import MemoryValue
from .op_size import OpSize
from .ea_mode import EAMode

MAX_MEMORY_LOCATION = 16777216  # 2^24

class M68K:
    def __init__(self):
        """
        Constructor
        """
        self.memory = Memory()

        # has the simulation been halted using SIMHALT or .halt()
        self.halted = False

        # should the clock automatically cycle?
        self.clock_auto_cycle = True
        self._clock_cycles = 0

        # todo add events for each clock cycle
        # this is necessary for implementing breakpoints
        # and watches for value changes

        # set up the registers to their default values
        self.registers = {}
        self.__init_registers()

    def __init_registers(self):
        """
        Set the registers to their default values
        :return:
        """

        # loop through all of the full size registers which are just 32 bits / 4 bytes long
        for register in FULL_SIZE_REGISTERS:
            self.registers[register] = MemoryValue(OpSize.LONG)

        # set up all of the odd registers (in this case, just the Condition Code Register)
        # which just uses 5 bits out of the lowermost byte (do we want to allocate it an entire word instead?)
        self.registers[Register.ConditionCodeRegister] = MemoryValue(OpSize.BYTE)

        # Easy68k initializes the step counter (A7) to 0x1000000 by default, so do the same
        self.set_register(Register.A7, MemoryValue(OpSize.LONG, unsigned_int=0x1000000))

    def get_register(self, register: Register) -> MemoryValue:
        """
        Gets the entire value of a register
        :param register:
        :return:
        """
        # from pprint import pprint
        # pprint(self.registers)

        # for keys in self.registers.keys():
        #     print(keys, self.registers[keys])
        return self.registers[register]

    def set_register(self, register: Register, val: MemoryValue):
        """
        Sets the value of a register using a 32-bit int
        :param register:
        :param val:
        :return:
        """
        assert isinstance(register, Register)
        # if the register is the CCR, use that method to handle setting it
        # because of its different size
        if register == Register.ConditionCodeRegister:
            self._set_condition_code_register_value(val)
            return

        # if the register is an address register that is limited to fit in the bounds of memory
        if register in ALL_ADDRESS_REGISTERS:
            self.set_address_register_value(register, val)
            return

        # now for all other registers
        # ensure that the value is within bounds
        # actual negative numbers will need to be converted into 32-bit numbers
        assert 0 <= val.get_value_unsigned() <= 0xFFFFFFFF, 'The value for registers must fit into 4 bytes!'

        # set the value
        self.registers[register] = val

    def _set_condition_code_register_value(self, val: MemoryValue):
        """
        Sets the value for the condition code register
        :param val:
        :return:
        """
        # ensure that the value is within bounds
        # since the CCR is just a single byte
        assert 0 <= val.get_value_unsigned() <= 0xFF, 'The value for the CCR must fit in a single byte!'

        # now set the value
        self.registers[Register.ConditionCodeRegister] = val

    def get_program_counter_value(self) -> int:
        """
        Gets the 32-bit unsigned integer value for the program counter value
        :return:
        """
        mv = self.get_register(Register.ProgramCounter)
        ret = mv.get_value_unsigned()
        return ret

    def set_address_register_value(self, reg: Register, new_value: MemoryValue):
        """
        Sets the value of an address register, so the PC or A0-A7
        :param reg:
        :param new_value:
        :return:
        """
        # no longer assert that the address register value is a pointer to memory
        # since address register direct modes don't consider the amount of memory
        assert reg in ALL_ADDRESS_REGISTERS, 'The register given is not an address register!'

        # now set the value of the register
        self.registers[reg].set_value_unsigned_int(new_value.get_value_unsigned())

    def set_program_counter_value(self, new_value: int):
        """
        Sets the value of the program counter
        Must be a non negative integer that is less than the maximum location size
        :param new_value:
        :return:
        """
        self.set_address_register_value(Register.ProgramCounter, MemoryValue(OpSize.LONG, unsigned_int=new_value))

    def increment_program_counter(self, inc: int):
        """
        Increments the program counter by the given value
        :param inc:
        :return:
        """
        self.set_program_counter_value(
            self.get_program_counter_value() + inc)

    def get_condition_status_code(self, code: ConditionStatusCode) -> bool:
        """
        Gets the status of a code from the Condition Code Register
        :param code:
        :return:
        """
        ccr = self.get_register(Register.CCR).get_value_unsigned()
        # ccr is only 1 byte, bit mask away the bit being looked for
        return (ccr & code) > 0

    def get_condition_status_code_flags(self) -> list:
        """
        Gets all of the CCR flags.
        """
        return 
        [
            self.get_condition_status_code(ConditionStatusCode.X),
            self.get_condition_status_code(ConditionStatusCode.N),
            self.get_condition_status_code(ConditionStatusCode.Z),
            self.get_condition_status_code(ConditionStatusCode.V),
            self.get_condition_status_code(ConditionStatusCode.C)
        ]

    def set_condition_status_code(self, code: ConditionStatusCode, value: bool):
        """
        Sets the status of a code from the Condition Code Register to value
        :param code:
        :return:
        """
        ccr = self.get_register(Register.CCR)
        v = ccr.get_value_unsigned()

        if value:
            v |= code
        else:
            v &= ~code

        self._set_condition_code_register_value(MemoryValue(OpSize.BYTE, unsigned_int=v))

    def run(self):
        """
        Starts the automatic execution
        :return:
        """
        # needs to be totally reworked
        if not self.halted:
            if not self.clock_auto_cycle:
                # run a single instruction
                self.step_instruction()
            else:
                while self.clock_auto_cycle:
                    self.step_instruction()

    def halt(self):
        """
        Halts the auto simulation execution
        :return:
        """
        print("HALT")
        self.print_debug()
        self.clock_auto_cycle = False
        self.halted = True

    def print_debug(self):
        """
        Prints out debug information.
        """
        print("----- debug info -----")
        c = 0
        for r in self.registers.keys():
            val = self.registers[r].get_value_unsigned()
            val = f"0x{val:x}" if r != Register.CCR else f"0b{val:8b}"
            if c % 2 == 0:
                print(f"{str(r)}:\t{val}\t", end='')
            else:
                print(f"{str(r)}:\t{val}")
            c += 1
        print()

    def step_instruction(self):
        """
        Increments the clock until the program
        counter increments
        :return:
        """
        if not self.halted:
            # get the PC location
            pc_val = self.get_program_counter_value()
            
            from .assemblers import assemblers
            from .binary_prefix_tree import BinaryPrefixTree
            assembler_tree = BinaryPrefixTree(assemblers)

            # get the value where the PC points to
            pc_op_val = self.memory.get(OpSize.WORD, pc_val)

            # workaround for null data
            if pc_op_val == 0:
                self.set_program_counter_value(pc_val + 2)
                self.halt()
                return

            # get the opcode for that value
            opcode_assembler = assembler_tree.get_assembler(pc_op_val)
            opcode_name = opcode_assembler.get_opcode()
            asm_values = opcode_assembler.disassemble_values(pc_op_val)

            from .opcodes import get_opcode

            try:
                op = get_opcode(opcode_name, asm_values)
                print(f"--- $0x{pc_val}: {pc_op_val} --- {opcode_name}")
                op.execute(self)
                pc_val += 2
                self.set_program_counter_value(pc_val)
            except AssertionError:
                print(f"--- $0x{pc_val}: {pc_op_val} --- {opcode_name} NOT IMPLEMENTED")
                # in this case we are unable to determine the size of any immediates
                # if any, so increment the pc by a word for now
                pc_val += 2
                self.set_program_counter_value(pc_val)

            # todo, need to increment the pc
            # this will depend on the size of immediates
        else:
            print("Tried to exec while halted")
            # # must be here or we get circular dependency issues
            # from .find_module import find_opcode_cls, valid_opcodes

            # for op_str in valid_opcodes:
            #     op_class = find_opcode_cls(op_str)

            #     # We don't know this opcode, there's no module for it
            #     if op_class is None:
            #         print('Opcode {} is not known: skipping and continuing'.format(op_str))
            #         assert False
            #         continue

            #     # 10 comes from 2 bytes for the op and max 2 longs which are each 4 bytes
            #     # note: this currently has the edge case that it will fail unintelligibly
            #     # if encountered at the end of memory
            #     pc_val = self.get_program_counter_value()
            #     op = op_class.disassemble_instruction(self.memory.memory[pc_val:pc_val+10])
            #     if op is not None:
            #         op.execute(self)
            #         # done exeucting after doing an operation
            #         return

    def reload_execution(self):
        """
        restarts execution of the program
        up to the current program counter location
        :return:
        """
        # get the current PC
        current_pc = self.get_program_counter_value()

        # reset the PC value
        # todo, need to store the starting location

        # set the starting PC value

        # run until hits that PC value

    def get_cycles(self):
        """
        Returns how many clock cycles have been performed
        :return:
        """
        return self._clock_cycles

    def clear_cycles(self):
        """
        Resets the count of clock cycles
        :return:
        """
        self._clock_cycles = 0

    def load_list_file(self, list_file: ListFile):
        """
        Load List File

        load the contents of a list file into memory
        using the locations specified inside of the list file
        :param list_file:
        :return:
        """
        self.memory.load_list_file(list_file)
        self.set_program_counter_value(int(list_file.starting_execution_address))

    def load_memory(self, file : typing.BinaryIO):
        """
        saves the raw memory into the designated file
        NOTE: file must be opened as binary or this won't work
        """
        self.memory.load_memory(file)

    def save_memory(self, file : typing.BinaryIO):
        """
        Loads the raw memory from the designated file
        This includes programs
        NOTE: file must be opened as binary or this won't work
        """
        self.memory.save_memory(file)

    def set_ccr_reg(self, extend, negative, zero, overflow, carry): 
        """
        Accepts Boolean values for X,N,Z,V, and C, respectively and sets the CCR accordingly.
        Passing None in for any argument will cause it to ignore that bit.
        Returns nothing.
        :param extend:
        :param negative:
        :param zero:
        :param overflow:
        :param carry:
        :return:
        """
        if extend is not None:
            extend = bool(extend)
            self.set_condition_status_code(ConditionStatusCode.X, extend)
            
        if negative is not None:
            negative = bool(negative)
            self.set_condition_status_code(ConditionStatusCode.N, negative)
            
        if zero is not None:
            zero = bool(zero)
            self.set_condition_status_code(ConditionStatusCode.Z, zero)
            
        if overflow is not None:
            overflow = bool(overflow)
            self.set_condition_status_code(ConditionStatusCode.V, overflow)
            
        if carry is not None:
            carry = bool(carry)
            self.set_condition_status_code(ConditionStatusCode.C, carry)
    
    def get_ea_value(self, ea: EAMode, location: int, size: OpSize = OpSize.WORD) -> MemoryValue:
        # location is either the referenced address or the register number
        if ea == EAMode.DRD:
            reg = Register.get_data_register(location)
            return self.get_register(reg)
        if ea == EAMode.IMM:
            imm_location = self.get_register(Register.PC).get_value_unsigned() + OpSize.WORD.value
            return self.memory.get(size, imm_location)
        if ea in [EAMode.ARIPI, EAMode.ARIPD, EAMode.ARI]:
            reg = Register.get_addr_register(location)
            address = self.get_register(reg)

            # handle post increment, pre decrement
            if ea == EAMode.ARIPI:
                new_address = MemoryValue(len=OpSize.WORD, unsigned_int=OpSize.WORD.value + address.get_value_unsigned())
                self.set_register(reg, new_address)
            elif ea == EAMode.ARIPD:
                new_address = MemoryValue(len=OpSize.WORD, unsigned_int=address.get_value_unsigned() - OpSize.WORD.value)
                self.set_register(reg, new_address)
                address = new_address
            return self.memory.get(self.size, address.get_value_unsigned())
        if ea == EAMode.ALA or ea == EAMode.AWA:
            if ea == EAMode.AWA:
                imm_location = self.get_register(Register.PC) + OpSize.WORD.value
            else:
                imm_location = self.get_register(Register.PC) + OpSize.LONG.value
            addr = MemoryValue(OpSize.WORD, unsigned_int=imm_location)
            location = self.memory.get(OpSize.WORD, addr).get_value_unsigned()
            return self.memory.get(size, locaiton)

    def set_ea_value(self, ea: EAMode, location: int, val: MemoryValue, size: OpSize = OpSize.WORD):
        if ea == EAMode.DRD:
            reg = Register.get_data_register(location)
            self.set_register(reg, val)
        elif ea == EAMode.IMM:
            imm_location = self.get_register(Register.PC).get_value_unsigned() + OpSize.WORD.value
            self.memory.set(size, imm_location, val)
        elif ea in [EAMode.ARIPI, EAMode.ARIPD, EAMode.ARI]:
            reg = Register.get_addr_register(location)
            address = self.set_register(reg, val)

            # handle post increment, pre decrement
            if ea == EAMode.ARIPI:
                new_address = MemoryValue(len=OpSize.WORD, unsigned_int=OpSize.WORD.value + address.get_value_unsigned())
                self.set_register(reg, new_address)
            elif ea == EAMode.ARIPD:
                new_address = MemoryValue(len=OpSize.WORD, unsigned_int=address.get_value_unsigned() - OpSize.WORD.value)
                self.set_register(reg, new_address)
                address = new_address
            self.memory.set(self.size, address.get_value_unsigned(), val)
        elif ea == EAMode.ALA or ea == EAMode.AWA:
            if ea == EAMode.AWA:
                imm_location = self.get_register(Register.PC) + OpSize.WORD.value
            else:
                imm_location = self.get_register(Register.PC) + OpSize.LONG.value
            addr = MemoryValue(OpSize.WORD, unsigned_int=imm_location)
            location = self.memory.set(OpSize.WORD, addr).get_value_unsigned()
            self.memory.set(size, location, val)