from typing import Union
from ..ea_mode import EAMode
from ..op_size import OpSize
from ..m68k import M68K
from .opcode import Opcode
from ..split_bits import split_bits
from ..assembly_parameter import AssemblyParameter
from ..memory_value import MemoryValue
from ..register import Register


class Rts(Opcode):
    """
    RTS: Return from Subroutine
    Operation: (SP) -> PC; SP + 4 -> SP
    Assembler Syntax: RTS
    Attributes: Unsized
    Description: Pulls the program counter value from the stack.
                 The previous program counter value is lost.
    Condition Codes: Not affected
    Instruction Format: 0100111001110101
    """
    def __init__(self):
        pass    # Doesn't need to do anything else

    def assemble(self) -> bytearray:
        """
        Assembles this opcode into hex to be inserted into memory
        :return: The hex version of this opcode
        """

        # 0100111001110101
        # ret_opcode is the binary value which represents the assembled instruction
        ret_opcode = 0b0100111001110101

        return bytearray(ret_opcode.to_bytes(OpSize.WORD.value, byteorder='big', signed=False))

    def execute(self, simulator: M68K):
        """
        Executes this command in a simulator
        :param simulator: The simulator to execute the command on
        :return: Nothing
        """

        # (SP) -> PC
        step_counter = 7  # Register A7 is SP
        sp_val = AssemblyParameter(EAMode.ARI, step_counter).get_value(simulator, OpSize.LONG)
        simulator.set_program_counter_value(sp_val.get_value_unsigned())

        # get the value of src from the simulator
        sp_val = simulator.get_register(Register.A7)
        # The address is a long word address
        new_sp_val = sp_val.get_value_unsigned() + OpSize.LONG.value

        # SP + 4 -> SP
        simulator.set_register(Register.A7, MemoryValue(OpSize.LONG, unsigned_int=new_sp_val))

    def __str__(self):
        # Makes this a bit easier to read in doctest output
        return 'Rts command'

    @classmethod
    def command_matches(cls, command: str) -> bool:
        """
        Checks whether a command string is an instance of this command type
        :param command: The command string to check (e.g. 'MOVE.B', 'LEA', etc.)
        :return: Whether the string is an instance of this command type
        """
        return opcode_util.command_matches(command, 'RTS')

    @classmethod
    def get_word_length(cls, command: str, parameters: str) -> int:
        """
        >>> Rts.get_word_length('RTS', '')
        1

        >>> Rts.get_word_length('RTS', '    ')
        1

        Gets what the end length of this command will be in memory
        :param command: The text of the command itself (e.g. "LEA", "MOVE.B", etc.)
        :param parameters: The parameters after the command
        :return: The length of the bytes in memory in words
        """
        # Ensure correct OPCODE
        assert command.strip(' ') == 'RTS'
        # OPCODE does not have any parameters
        assert parameters is None or parameters.strip(' ') == ""
        return 1

    @classmethod
    def is_valid(cls, command: str, parameters: str) -> (bool, list):
        """
        Tests whether the given command is valid

        >>> Rts.is_valid('RTS', '')[0]
        True

        >>> Rts.is_valid('RTS', '(A5)')[0]
        False

        >>> Rts.is_valid('RTS', '#5, D1')[0]
        False

        >>> Rts.is_valid('RTS.W', '(A1)')[0]
        False

        >>> Rts.is_valid('RT', '($1000).W')[0]
        False

        >>> Rts.is_valid('RTS.', '(A4)')[0]
        False

        >>> Rts.is_valid('RTS', '($7000).W')[0]
        False

        :param command: The command itself (e.g. 'MOVE.B', 'LEA', etc.)
        :param parameters: The parameters after the command
                           (such as the source and destination of a move)
        :return: Whether the given command is valid and a list of issues/warnings encountered
        """
        issues = []
        try:
            assert opcode_util.check_valid_command(command, 'RTS', can_take_size=False), 'RTS Command invalid'
            assert not parameters.strip(), 'RTS takes no parameters'

            return True, issues
        except AssertionError as error:
            issues.append((error.args[0], 'ERROR'))
            return False, issues

    @classmethod
    def disassemble_instruction(cls, data: bytearray) -> Union[Opcode, None]:
        """
        This has a non-RTS opcode
        >>> Rts.disassemble_instruction(bytearray.fromhex('0280'))


        RTS
        >>> op = Rts.disassemble_instruction(bytearray.fromhex('4E75'))

        >>> str(op)
        'Rts command'

        Parses some raw data into an instance of the opcode class
        :param data: The data used to convert into an opcode instance
        :return: The constructed instance or none if there was an error and
            the amount of data in words that was used (e.g. extra for immediate
            data) or 0 for not a match
        """
        assert len(data) == 2, 'Opcode size is only one word'

        first_word = int.from_bytes(data[0:2], 'big')

        [opcode_bin] = split_bits(first_word, [16])

        if opcode_bin != 0b0100111001110101:
            return None

        return cls()

    @classmethod
    def from_str(cls, command: str, parameters: str):
        """
        Parses a RTS command from text.

        >>> str(Rts.from_str('RTS', ''))
        'Rts command'

        :param command: The command itself (e.g. 'MOVE.B', 'LEA', etc.)
        :param parameters: The parameters after the command
                           (such as the source and destination of a move)
        :return: The parsed command
        """
        # Ensure correct OPCODE
        assert command.strip(' ') == 'RTS'
        # OPCODE does not have any parameters
        assert parameters is None or parameters.strip(' ') == ""

        return cls()
