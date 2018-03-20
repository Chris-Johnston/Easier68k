from ..opcodes.opcode import Opcode
from ...simulator.m68k import M68K
from ..util.parsing import parse_assembly_parameter, from_str_util
from ..util.split_bits import split_bits
from ..models.trap_vector import TrapVector
from ..enum.trap_task import TrapTask
from ..enum.register import Register
from ..enum.op_size import OpSize
from ..util.input import get_input
from ..enum.trap_vector import TrapVectors

class Trap(Opcode): # forward declaration
    pass

class Trap(Opcode):

    def __init__(self, param: TrapVectors):
        assert isinstance(param, TrapVectors)
        # max size is 4 bit
        assert 0 <= param.value <= 0b1111
        self.trpVector = param

        # flags to use so that this can be tested easier
        self.use_debug_input = False
        self.debug_input = 'debug input'

    def assemble(self) -> bytearray:
        """
        Assembles this opcode into hex to be inserted
        into memory
        :return:
        """
        # the bottom 4 bits are set to 0
        value = 0b0100111001000000
        # mask the task to fit in 4 bits
        masked = self.trpVector.value & 0b1111
        # add the masked bits
        value |= masked
        # convert this value into a bytearray of len = 1 word
        return value.to_bytes(2, byteorder='big', signed=False)


    def execute(self, simulator: M68K):
        """
        Executes this command in a simulator
        :param simulator:
        :return:
        """
        if self.trpVector.value == TrapVectors.IO:

            task = TrapTask(simulator.get_register_value(Register.D0))

            if task is TrapTask.DisplayNullTermString:

                # get the value of A1
                location = simulator.get_register_value(Register.A1)
                value = int.from_bytes(simulator.memory.get(1, location), byteorder='big', signed=False)
                while value != 0:
                    print(chr(value), end='')
                    location += 1
                    value = int.from_bytes(simulator.memory.get(1, location), byteorder='big', signed=False)

            if task is TrapTask.DisplayNullTermStringWithCRLF:
                # get the value of A1
                location = simulator.get_register_value(Register.A1)
                value = int.from_bytes(simulator.memory.get(1, location), byteorder='big', signed=False)
                while value != 0:
                    print(chr(value), end='')
                    location += 1
                    value = int.from_bytes(simulator.memory.get(1, location), byteorder='big', signed=False)
                print('')

            if task is TrapTask.DisplayNullTermStringAndReadNumberFromKeyboard:
                # get the value of A1
                location = simulator.get_register_value(Register.A1)
                value = int.from_bytes(simulator.memory.get(1, location), byteorder='big', signed=False)
                while value != 0:
                    print(chr(value), end='')
                    location += 1
                    value = int.from_bytes(simulator.memory.get(1, location), byteorder='big', signed=False)

                # read a number from the keyboard

            if task is TrapTask.DisplaySignedNumber:
                # get the value of D1.L
                value = simulator.get_register(Register.D1)
                int_val = int.from_bytes(value, byteorder='big', signed=True)
                print(int_val, end='')

            if task is TrapTask.DisplaySingleCharacter:
                # get the value of D1.B
                value = simulator.get_register_value(Register.D1)
                # mask it
                value = 0xFF & value
                print(chr(value), end='')

            if task is TrapTask.Terminate:
                # same as SIMHALT
                simulator.halt()

        # increment the program counter
        simulator.increment_program_counter(OpSize.WORD.value)


    def __str__(self):
        return 'TRAP {}'.format(self.trpVector)

    @classmethod
    def from_str(cls, command: str, parameters: str):
        """
        Parses a TRAP command from text

        >>> str(Trap.from_str('TRAP', '#15'))
        'TRAP 15'

        >>> str(Trap.from_str('trap', '#%1111'))
        'TRAP 15'

        :param command:
        :param parameters:
        :return:
        """

        assert command.upper() == 'TRAP'

        # dont care about the size and parts values
        size, params, parts = from_str_util(command, parameters)

        assert len(params) == 1

        return cls(TrapVectors.parse(params[0]))

    @classmethod
    def disassemble_instruction(cls, data: bytearray) -> Opcode:
        """
        Parses raw data into an instance of Trap
        :param data:
        :return:
        """
        if len(data) < 2:
            return None  # len must be at least 1 word

        first_word = int.from_bytes(data[0:2], byteorder='big')

        [opcode_bin, task_num] = split_bits(
            first_word,
            [12, 4])

        # didnt match
        if opcode_bin != 0b010011100100:
            return None

        # dont need to check that the size is valid, within 4 bits is ok
        # though some may not do anything

        return cls(TrapVectors(task_num))

    @classmethod
    def is_valid(cls, command: str, parameters: str) -> (bool, list):
        """
        Tests whether the given command is valid
        :param command:
        :param parameters:
        :return:
        """

        # dont care about the size and parts values
        size, params, parts = from_str_util(command, parameters)

        # have it parse, but not return value, just
        # check that it works
        try:
            TrapVector.parse(params[0])
        except:
            return False
        return (command.strip().upper() == 'TRAP' and len(params) == 1, [])  # TODO: Convert to actually return issues

    @classmethod
    def get_word_length(cls, command: str, parameters: str) -> int:
        """
        Get the length in words that this will take up in memory
        :param command:
        :param parameters:
        :return:
        """
        # always 1
        return 1

    @classmethod
    def command_matches(cls, command: str) -> bool:
        """
        Checks if a command string matches
        :param command:
        :return:
        """
        return command.upper() == 'TRAP'