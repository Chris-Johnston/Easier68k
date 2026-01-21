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
        return self.registers[register]

    def set_register(self, register: Register, val: MemoryValue):
        """
        Sets the value of a register using a 32-bit int
        :param register:
        :param val:
        :return:
        """
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
        self.clock_auto_cycle = False
        self.halted = True

    def step_instruction(self):
        """
        Increments the clock until the program
        counter increments
        :return:
        """
        if not self.halted:
            # must be here or we get circular dependency issues
            from .find_module import find_opcode_cls, valid_opcodes

            for op_str in valid_opcodes:
                op_class = find_opcode_cls(op_str)

                # We don't know this opcode, there's no module for it
                if op_class is None:
                    print('Opcode {} is not known: skipping and continuing'.format(op_str))
                    assert False
                    continue

                # 10 comes from 2 bytes for the op and max 2 longs which are each 4 bytes
                # note: this currently has the edge case that it will fail unintelligibly
                # if encountered at the end of memory
                pc_val = self.get_program_counter_value()
                op = op_class.disassemble_instruction(self.memory.memory[pc_val:pc_val+10])
                if op is not None:
                    op.execute(self)
                    # done exeucting after doing an operation
                    return

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
    
