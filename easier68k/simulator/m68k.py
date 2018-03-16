"""
Motorola 68k chip definition
"""

from .memory import Memory
from ..core.enum.register import Register, FULL_SIZE_REGISTERS, MEMORY_LIMITED_ADDRESS_REGISTERS
from ..core.enum.condition_status_code import ConditionStatusCode
from ..core.models.list_file import ListFile
import typing

MAX_MEMORY_LOCATION = 16777216  # 2^24

class M68K:
    def __init__(self):
        """
        Constructor
        """
        self.memory = Memory()

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
            self.registers[register] = bytearray(4)

        # set up all of the odd registers (in this case, just the Condition Code Register)
        # which just uses 5 bits out of the lowermost byte (do we want to allocate it an entire word instead?)
        self.registers[Register.ConditionCodeRegister] = bytearray(1)

    def get_register(self, register: Register) -> bytearray:
        """
        Gets the entire value of a register
        :param register:
        :return:
        """
        return self.registers[register]

    def get_register_value(self, register: Register) -> int:
        """
        Return the value contained in a register as a 32-bit unsigned integer
        :param register:
        :return:
        """
        # convert the contents of the byte array to hex, and then convert
        # that into an int
        return int(self.get_register(register).hex(), 16)

    def set_register_value(self, register: Register, val: int):
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
        if register in MEMORY_LIMITED_ADDRESS_REGISTERS:
            self.set_address_register_value(register, val)
            return

        # now for all other registers
        # ensure that the value is within bounds
        # actual negative numbers will need to be converted into 32-bit numbers
        assert 0 <= val <= 0xFFFFFFFF, 'The value for registers must fit into 4 bytes!'

        # set the value
        self.registers[register] = bytearray(val.to_bytes(4, 'big'))

    def _set_condition_code_register_value(self, val: int):
        """
        Sets the value for the condition code register
        :param val:
        :return:
        """
        # ensure that the value is within bounds
        # since the CCR is just a single byte
        assert 0 <= val <= 0xFF, 'The value for the CCR must fit in a single byte!'

        # now set the value
        self.registers[Register.ConditionCodeRegister] = bytearray(val.to_bytes(1, 'big'))


    def get_program_counter_value(self) -> int:
        """
        Gets the 32-bit integer value for the program counter value
        :return:
        """
        return self.get_register_value(Register.ProgramCounter)


    def set_address_register_value(self, reg: Register, new_value: int):
        """
        Sets the value of an address register, so the PC or A0-A7
        :param reg:
        :param new_value:
        :return:
        """
        assert 0 <= new_value <= MAX_MEMORY_LOCATION, 'The value of address registers must be in the range [0, 2^24]'
        assert reg in MEMORY_LIMITED_ADDRESS_REGISTERS, 'The register given is not an address register!'

        # now set the value of the register
        self.registers[reg] = bytearray(new_value.to_bytes(4, 'big'))


    def set_program_counter_value(self, new_value: int):
        """
        Sets the value of the program counter
        Must be a non negative integer that is less than the maximum location size
        :param new_value:
        :return:
        """
        self.set_address_register_value(Register.ProgramCounter, new_value)

    def get_condition_status_code(self, code: ConditionStatusCode) -> bool:
        """
        Gets the status of a code from the Condition Code Register
        :param code:
        :return:
        """
        ccr = self.get_register(Register.CCR)
        # ccr is only 1 byte, bit mask away the bit being looked for
        return (ccr[0] & code) > 0


    def run(self):
        """
        Starts the automatic execution
        :return:
        """
        pass

    def step_clock(self):
        """
        Increments the clock by a single cycle
        :return:
        """
        pass

    def step_instruction(self):
        """
        Increments the clock until the program
        counter increments
        :return:
        """
        # must be here or we get circular dependency issues
        from ..core.util.find_module import find_opcode_cls, valid_opcodes

        for op_str in valid_opcodes:
            op_class = find_opcode_cls(op_str)

            # We don't know this opcode, there's no module for it
            if op_class is None:
                print('Opcode {} is not known: skipping and continuing'.format(op_str))
                continue

            PC = self.get_program_counter_value()
            
            # 10 comes from 2 bytes for the op and max 2 longs which are each 4 bytes
            # note: this currently has the edge case that it will fail unintelligibly
            # if encountered at the end of memory
            op, words_read = op_class.from_binary(self.memory.memory[PC:PC+10])
            if op != None:
                op.execute(self)
                self.set_program_counter_value(PC + words_read*2)



    def reload_execution(self):
        """
        restarts execution of the program
        up to the current program counter location
        :return:
        """
        pass

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
