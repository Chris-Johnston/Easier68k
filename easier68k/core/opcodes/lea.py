from ...core.enum.ea_mode import EAMode
from ...core.enum import ea_mode_bin
from ...simulator.m68k import M68K
from ...core.opcodes.opcode import Opcode
from ...core.util import opcode_util
from ...core.enum.op_size import OpSize
from ..util.parsing import parse_assembly_parameter


class Lea(Opcode):
    pass


class Lea(Opcode):

    def __init__(self, src: EAMode, dest: EAMode):
        # Can't take data register, address register, or ARI with modifications
        assert src.mode not in [EAMode.DRD, EAMode.ARD, EAMode.ARIPD, EAMode.ARIPI, EAMode.IMM]
        self.src = src

        # Check that the destination is of a proper type
        assert dest.mode == EAMode.ARD  # Can only take address register direct
        self.dest = dest

    def assemble(self) -> bytearray:
        """
        Assembles this opcode into hex to be inserted into memory
        :return: The hex version of this opcode
        """
        # Create a binary string to append to, which we'll convert to hex at the end
        tr = '0100'  # Opcode
        tr += '{0:03b}'.format(self.dest.data)
        tr += '111'
        tr += ea_mode_bin.parse_from_ea_mode_modefirst(self.src)  # Source second
        # Append after the command
        # Size doesn't matter if it's not an immediate so we'll just give it W
        tr += opcode_util.ea_to_binary_post_op(self.src, 'L' if self.src.mode == EAMode.ALA else 'W')

        to_return = bytearray.fromhex(hex(int(tr, 2))[2:])  # Convert to a bytearray
        return to_return

    def execute(self, simulator: M68K):
        """
        Executes this command in a simulator
        :param simulator: The simulator to execute the command on
        :return: Nothing
        """
        self.dest.set_value(simulator, self.src.data, OpSize.LONG.get_number_of_bytes())

    def __str__(self):
        # Makes this a bit easier to read in doctest output
        return 'LEA command: src {}, dest {}'.format(self.src, self.dest)

    @classmethod
    def command_matches(cls, command: str) -> bool:
        """
        Checks whether a command string is an instance of this command type
        :param command: The command string to check (e.g. 'MOVE.B', 'LEA', etc.)
        :return: Whether the string is an instance of this command type
        """
        return opcode_util.command_matches(command, 'LEA')

    @classmethod
    def get_word_length(cls, command: str, parameters: str) -> int:
        """
        >>> Lea.get_word_length('LEA', '(A0), A1')
        1

        >>> Lea.get_word_length('LEA', '#$90, A0')
        2

        >>> Lea.get_word_length('LEA', '#$ABCDE, A0')
        3

        >>> Lea.get_word_length('LEA', '($AAAA).L, A6')
        3

        >>> Lea.get_word_length('LEA', '($AAAA).W, A5')
        2

        Gets what the end length of this command will be in memory
        :param command: The text of the command itself (e.g. "LEA", "MOVE.B", etc.)
        :param parameters: The parameters after the command
        :return: The length of the bytes in memory in words, as well as a list of warnings or errors encountered
        """
        valid, issues = cls.is_valid(command, parameters)
        if not valid:
            return 0
        # We can forego asserts in here because we've now confirmed this is valid assembly code

        # Split the parameters into EA modes
        params = parameters.split(',')

        if len(params) != 2:  # We need exactly 2 parameters
            issues.append(('Invalid syntax (missing a parameter/too many parameters)', 'ERROR'))
            return 0, issues

        src = parse_assembly_parameter(params[0].strip())  # Parse the source and make sure it parsed right
        dest = parse_assembly_parameter(params[1].strip())

        length = 1  # Always 1 word not counting additions to end

        if src.mode == EAMode.IMM:  # If we're moving an immediate we have to append the value afterwards
            if len(hex(src.data)[2:]) > 4:
                length += 2
            else:
                length += 1

        if src.mode == EAMode.AWA:  # Appends a word
            length += 1

        if src.mode == EAMode.ALA:  # Appends a long, so 2 words
            length += 2

        if dest.mode == EAMode.AWA:  # Appends a word
            length += 1

        if dest.mode == EAMode.ALA:  # Appends a long, so 2 words
            length += 2

        return length

    @classmethod
    def is_valid(cls, command: str, parameters: str) -> (bool, list):
        """
        Tests whether the given command is valid

        >>> Lea.is_valid('LEA', '(A0), A1')[0]
        True

        >>> Lea.is_valid('LEA', 'A0')[0]
        False

        >>> Lea.is_valid('LEA.B', '(A0), A1')[0]
        False

        >>> Lea.is_valid('LEA', 'D0, A2')[0]
        False

        >>> Lea.is_valid('LEA', '#$0A, A4')[0]
        True

        >>> Lea.is_valid('LEA', '($AAAA).L, A7')[0]
        True

        :param command: The command itself (e.g. 'MOVE.B', 'LEA', etc.)
        :param parameters: The parameters after the command (such as the source and destination of a move)
        :return: Whether the given command is valid and a list of issues/warnings encountered
        """
        issues = []
        try:
            assert opcode_util.check_valid_command(command, 'LEA', can_take_size=False), 'Command invalid'

            # Split the parameters into EA modes
            params = parameters.split(',')
            assert len(params) == 2, 'Must have two parameters'

            src = parse_assembly_parameter(params[0].strip())  # Parse the source and make sure it parsed right
            assert src, 'Error parsing src'

            dest = parse_assembly_parameter(params[1].strip())
            assert dest, 'Error parsing dest'

            assert src.mode not in [EAMode.DRD, EAMode.ARD, EAMode.ARIPD, EAMode.ARIPI], 'Invalid addressing mode'
            assert dest.mode == EAMode.ARD, 'Invalid addressing mode'

            return True, issues
        except AssertionError as e:
            issues.append((e.args[0], 'ERROR'))
            return False, issues

    @classmethod
    def from_binary(cls, data: bytearray) -> (Lea, int):
        """
        Parses some raw data into an instance of the opcode class

        :param data: The data used to convert into an opcode instance
        :return: The constructed instance or none if there was an error and
            the amount of data in words that was used (e.g. extra for immediate
            data) or 0 for not a match
        """
        return cls(parse_assembly_parameter('(A0)'), parse_assembly_parameter('A0')), 1  # TODO: Make this proper!

    @classmethod
    def from_str(cls, command: str, parameters: str):
        """
        Parses a LEA command from memory.

        >>> str(Lea.from_str('LEA', '(A0), A1'))
        'LEA command: src EA Mode: EAMode.ARI, Data: 0, dest EA Mode: EAMode.ARD, Data: 1'

        >>> str(Lea.from_str('LEA', '($0A).W, A2'))
        'LEA command: src EA Mode: EAMode.AWA, Data: 10, dest EA Mode: EAMode.ARD, Data: 2'

        :param command: The command itself (e.g. 'MOVE.B', 'LEA', etc.)
        :param parameters: The parameters after the command (such as the source and destination of a move)
        """
        valid, issues = cls.is_valid(command, parameters)
        if not valid:
            return None
        # We can forego asserts in here because we've now confirmed this is valid assembly code

        # Split the parameters into EA modes
        params = parameters.split(',')
        src = parse_assembly_parameter(params[0].strip())
        dest = parse_assembly_parameter(params[1].strip())

        return cls(src, dest)
