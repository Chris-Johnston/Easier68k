from ...simulator.m68k import M68K
from ...core.opcodes.opcode import Opcode
from ...core.util import opcode_util
from ..enum.op_size import OpSize


class Simhalt(Opcode):
    pass


class Simhalt(Opcode):
    def __init__(self):
        pass  # Nothing to initialize: SIMHALT is parameterless

    def assemble(self) -> bytearray:
        """
        Assembles this opcode into hex to be inserted into memory
        :return: The hex version of this opcode
        """
        return bytearray.fromhex('FFFFFFFF')

    def execute(self, simulator: M68K):
        """
        Executes this command in a simulator
        :param simulator: The simulator to execute the command on
        :return: Nothing
        """
        # make the simulator halt
        simulator.halt()

        # increment the program counter
        simulator.increment_program_counter(OpSize.LONG.value)

    def __str__(self):
        # Makes this a bit easier to read in doctest output
        return 'SIMHALT command'

    @classmethod
    def command_matches(cls, command: str) -> bool:
        """
        Checks whether a command string is an instance of this command type
        :param command: The command string to check (e.g. 'MOVE.B', 'LEA', etc.)
        :return: Whether the string is an instance of this command type
        """
        return opcode_util.command_matches(command, 'SIMHALT')

    @classmethod
    def get_word_length(cls, command: str, parameters: str) -> int:
        """
        >>> Simhalt.get_word_length('SIMHALT', '')
        2

        Gets what the end length of this command will be in memory
        :param command: The text of the command itself (e.g. "LEA", "MOVE.B", etc.)
        :param parameters: The parameters after the command
        :return: The length of the bytes in memory in words
        """
        valid, issues = Simhalt.is_valid(command, parameters)
        if not valid:
            return 0
        # We can forego asserts in here because we've now confirmed this is valid assembly code

        return 2

    @classmethod
    def is_valid(cls, command: str, parameters: str) -> (bool, list):
        """
        Tests whether the given command is valid

        >>> Simhalt.is_valid('SIMHALT', '')[0]
        True

        >>> Simhalt.is_valid('SIMHALT.B', '')[0]
        False

        >>> Simhalt.is_valid('MOVE', '')[0]
        False

        >>> Simhalt.is_valid('SIMHALT', ' ')[0]
        True

        >>> Simhalt.is_valid('SIMHALT', 'D0')[0]
        False

        :param command: The command itself (e.g. 'MOVE.B', 'LEA', etc.)
        :param parameters: The parameters after the command (such as the source and destination of a move)
        :return: Whether the given command is valid and a list of issues/warnings encountered
        """
        issues = []
        try:
            assert opcode_util.check_valid_command(command, 'SIMHALT', can_take_size=False), 'Command invalid'
            assert not parameters.strip(), 'SIMHALT takes no parameters'

            return True, issues
        except AssertionError as e:
            issues.append((e.args[0], 'ERROR'))
            return False, issues

    @classmethod
    def disassemble_instruction(cls, data: bytearray) -> Opcode:
        """
        Parses some raw data into an instance of the opcode class

        :param data: The data used to convert into an opcode instance
        :return: The constructed instance or none if there was an error and
            the amount of data in words that was used (e.g. extra for immediate
            data) or 0 for not a match
        """
        return cls()

    @classmethod
    def from_str(cls, command: str, parameters: str):
        """
        Parses a SIMHALT command from memory.

        >>> str(Simhalt.from_str('SIMHALT', ''))
        'SIMHALT command'

        :param command: The command itself (e.g. 'MOVE.B', 'LEA', etc.)
        :param parameters: The parameters after the command (such as the source and destination of a move)
        """
        return cls()
