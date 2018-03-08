from ...core.enum.ea_mode import EAMode
from ...core.enum.op_size import MoveSize
from ...core.enum.ea_mode_bin import EAModeBinary
from ...simulator.m68k import M68K
from ...core.opcodes.opcode import Opcode


class Move(Opcode):
    pass


class Move(Opcode):
    # Allowed values: nothing, or some combination of B, W, and L (for byte, word, and long)
    # For example, MOVE would have 'BWL' because it can operate on any size of data, while MOVEA would have 'WL' because
    # it can't operate on byte-sized data
    allowed_sizes = 'BWL'

    def __init__(self, command: str, parameters: str):
        """
        >>> str(Move('MOVE.B', '-(A0), D1'))
        'Move command: Size B, src Mode: 4, Data: 0, dest Mode: 0, Data: 1'

        >>> str(Move('MOVE.L', 'D3, (A0)'))
        'Move command: Size L, src Mode: 0, Data: 3, dest Mode: 2, Data: 0'

        >>> Move('MOVE.W', 'D3, A3')
        Traceback (most recent call last):
        ...
        AssertionError

        :param command:
        :param parameters:
        """
        parts = command.split('.')  # Split the command by period to get the size of the command
        assert len(parts) <= 2  # If we have more than 2 parts something is seriously wrong
        if len(parts) == 1:  # Use the default size
            size = 'W'
        else:
            assert parts[1] in Move.allowed_sizes, "Size {} isn't allowed for command {}".format(parts[1], command[0])
            size = parts[1]

        # Split the parameters into EA modes
        params = parameters.split(',')
        assert len(params) == 2

        src = EAMode.parse_ea(params[0].strip())  # Parse the source and make sure it parsed right
        assert src.mode > EAMode.ERR, 'Error parsing src'  # -1 means error

        dest = EAMode.parse_ea(params[1].strip())
        assert dest.mode > EAMode.ERR, 'Error parsing dest'  # -1 means error

        Move.__init__(self, src, dest, size)

    # Include parameters here
    def __init__(self, src: EAMode, dest: EAMode, size='Ws'):
        # Check that the src is of the proper type (for example, can't move from an address register for a move command)
        assert src.mode != EAMode.ARD  # Only invalid src is address register direct
        self.src = src

        # Check that the destination is of a proper type
        assert dest.mode != EAMode.ARD and dest.mode != EAMode.IMM  # Can't take address register direct or immediates
        self.dest = dest

        # Check that this is a valid size (for example, 'MOVEA.B' is not a valid command)
        assert size in Move.allowed_sizes
        self.size = size

    def assemble(self) -> bytearray:
        # Create a binary string to append to, which we'll convert to hex at the end
        tr = '00'  # Opcode
        tr += '{0:02d}'.format(MoveSize.parse(self.size))  # Size bits
        tr += EAModeBinary.parse_from_ea_mode_xnfirst(self.dest)  # Destination first
        tr += EAModeBinary.parse_from_ea_mode_mfirst(self.src)  # Source second

        to_return = bytearray.fromhex(hex(int(tr, 2))[2:])  # Convert to a bytearray
        return to_return

    def execute(self, simulator: M68K):
        pass

    def __str__(self):
        # Makes this a bit easier to read in doctest output
        return 'Move command: Size {}, src {}, dest {}'.format(self.size, self.src, self.dest)

    @staticmethod
    def is_valid(command: str, parameters: str) -> (bool, list):
        """
        Tests whether the given command is valid

        >>> Move.is_valid('MOVE.B', 'D0, D1')[0]
        True

        >>> Move.is_valid('MOVE.W', 'D0')[0]
        False

        >>> Move.is_valid('MOVE.G', 'D0, D1')[0]
        False

        >>> Move.is_valid('MOVE.L', 'D0, A2')[0]
        False

        :param command: The command itself (e.g. 'MOVE.B', 'LEA', etc.)
        :param parameters: The parameters after the command (such as the source and destination of a move)
        :return: Whether the given command is valid and a list of issues/warnings encountered
        """
        issues = []
        parts = command.split('.')  # Split the command by period to get the size of the command
        assert len(parts) <= 2  # If we have more than 2 parts something is seriously wrong
        if len(parts) != 1:  # Has a size specifier
            try:
                assert parts[1] in Move.allowed_sizes, "Size {} isn't allowed for command {}".format(parts[1], command[0])
            except AssertionError as e:
                issues.append((e.args[0], 'ERROR'))
                return False, issues

        # Split the parameters into EA modes
        try:
            params = parameters.split(',')
            assert len(params) == 2, 'Must have two parameters'
        except AssertionError as e:
            issues.append((e.args[0], 'ERROR'))
            return False, issues

        try:
            src = EAMode.parse_ea(params[0].strip())  # Parse the source and make sure it parsed right
            assert src.mode > EAMode.ERR, 'Error parsing src'  # -1 means error
        except AssertionError as e:
            issues.append((e.args[0], 'ERROR'))
            return False, issues

        try:
            dest = EAMode.parse_ea(params[1].strip())
            assert dest.mode > EAMode.ERR, 'Error parsing dest'  # -1 means error
        except AssertionError as e:
            issues.append((e.args[0], 'ERROR'))
            return False, issues

        try:
            assert src.mode != EAMode.ARD, 'Invalid addressing mode'  # Only invalid src is address register direct
            assert dest.mode != EAMode.ARD and dest.mode != EAMode.IMM, 'Invalid addressing mode'
        except AssertionError as e:
            issues.append((e.args[0], 'ERROR'))
            return False, issues

        return True, issues

    @staticmethod
    def get_word_length(command: str, parameters: str) -> (int, list):
        """
        >>> Move.get_word_length('MOVE', 'D0, D1')
        (1, [])

        >>> Move.get_word_length('MOVE.L', '#$90, D3')
        (3, [])

        >>> Move.get_word_length('MOVE.W', '#$90, D3')
        (2, [])

        >>> Move.get_word_length('MOVE.W', '($AAAA).L, D7')
        (3, [])

        Gets what the end length of this command will be in memory
        :param command: The text of the command itself (e.g. "LEA", "MOVE.B", etc.)
        :param parameters: The parameters after the command
        :return: The length of the bytes in memory in words, as well as a list of warnings or errors encountered
        """

        issues = []  # Set up our issues list (warnings + errors)
        parts = command.split('.')  # Split the command by period to get the size of the command
        assert len(parts) <= 2  # If we have more than 2 parts something is seriously wrong
        if len(parts) == 1:  # Use the default size
            size = 'W'
        else:
            # Parse the size of the command and make sure it's legal
            assert parts[1] in Move.allowed_sizes, "Size {} isn't allowed for command {}".format(parts[1], command[0])
            size = parts[1]

        # Split the parameters into EA modes
        params = parameters.split(',')
        if len(params) != 2:  # We need exactly 2 parameters
            issues.append(('Invalid syntax (missing a parameter/too many parameters)', 'ERROR'))
            return 0, issues

        try:
            src = EAMode.parse_ea(params[0].strip())  # Parse the source and make sure it parsed right
            assert src.mode > EAMode.ERR, 'Error parsing src'  # -1 means error
            assert src.mode != EAMode.ARD, 'Invalid addressing mode'  # Only invalid src is address register direct
        except AssertionError:
            issues.append(('Error parsing source', 'ERROR'))
            return 0, issues

        try:
            dest = EAMode.parse_ea(params[1].strip())
            assert dest.mode > EAMode.ERR, 'Error parsing dest'  # -1 means error
            # Can't take address register direct or immediates
            assert dest.mode != EAMode.ARD and dest.mode != EAMode.IMM, 'Invalid addressing mode'
        except AssertionError:
            issues.append(('Error parsing destination', 'ERROR'))
            return 0, issues

        length = 1  # Always 1 word not counting additions to end

        if src.mode == EAMode.IMM:  # If we're moving an immediate we have to append the value afterwards
            if size == 'L':
                length += 2  # Longs are 2 words long
            else:
                length += 1  # This is a word or byte, so only 1 word

        if src.mode == EAMode.AWA:  # Appends a word
            length += 1

        if src.mode == EAMode.ALA:  # Appends a long, so 2 words
            length += 2

        return length, issues

