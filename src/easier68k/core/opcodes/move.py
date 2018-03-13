"""
>>> str(Move.from_str('MOVE.B', '-(A0), D1')[0])
'Move command: Size B, src EA Mode: EAMode.ARIPD, Data: 0, dest EA Mode: EAMode.DRD, Data: 1'

>>> str(Move.from_str('MOVE.L', 'D3, (A0)')[0])
'Move command: Size L, src EA Mode: EAMode.DRD, Data: 3, dest EA Mode: EAMode.ARI, Data: 0'

>>> Move.from_str('MOVE.W', 'D3, A3')[1]
[('Invalid addressing mode', 'ERROR')]
"""
from ...core.enum.ea_mode import EAMode
from ...core.enum.op_size import MoveSize
from ...core.enum.ea_mode_bin import EAModeBinary, parse_ea_from_binary
from ...simulator.m68k import M68K
from ...core.opcodes.opcode import Opcode
from ...core.util.split_bits import split_bits
from ...core.util.conversions import get_number_of_bytes
from ..util.parsing import parse_assembly_parameter


class Move(Opcode):
    # Allowed values: nothing, or some combination of B, W, and L (for byte, word, and long)
    # For example, MOVE would have 'BWL' because it can operate on any size of data, while MOVEA would have 'WL' because
    # it can't operate on byte-sized data
    allowed_sizes = 'BWL'
    
    # same as above, but for dissassembly
    allowed_sizes_binary = [MoveSize.parse(x) for x in allowed_sizes]

    @classmethod
    def from_str(cls, command: str, parameters: str):
        """
        Parses a MOVE command from memory.

        :param command: The command itself (e.g. 'MOVE.B', 'LEA', etc.)
        :param parameters: The parameters after the command (such as the source and destination of a move)
        """
        valid, issues = Move.is_valid(command, parameters)
        if not valid:
            return None, issues
        # We can forego asserts in here because we've now confirmed this is valid assembly code

        parts = command.split('.')  # Split the command by period to get the size of the command
        if len(parts) == 1:  # Use the default size
            size = 'W'
        else:
            size = parts[1].upper()

        # Split the parameters into EA modes
        params = parameters.split(',')

        src = parse_assembly_parameter(params[0].strip())
        dest = parse_assembly_parameter(params[1].strip())

        return cls(src, dest, size), issues

        

    def __init__(self, src: EAMode, dest: EAMode, size='W'):
        # Check that the src is of the proper type (for example, can't move from an address register for a move command)
        assert src.mode != EAMode.ARD  # Only invalid src is address register direct
        self.src = src

        # Check that the destination is of a proper type
        assert dest.mode != EAMode.ARD and dest.mode != EAMode.IMM  # Can't take address register direct or immediates
        self.dest = dest

        # Check that this is a valid size (for example, 'MOVEA.B' is not a valid command)
        assert size.upper() in Move.allowed_sizes
        self.size = size

    def assemble(self) -> bytearray:
        """
        Assembles this opcode into hex to be inserted into memory
        :return: The hex version of this opcode
        """
        # Create a binary string to append to, which we'll convert to hex at the end
        tr = '00'  # Opcode
        tr += '{0:02d}'.format(MoveSize.parse(self.size))  # Size bits
        tr += EAModeBinary.parse_from_ea_mode_xnfirst(self.dest)  # Destination first
        tr += EAModeBinary.parse_from_ea_mode_mfirst(self.src)  # Source second

        to_return = bytearray.fromhex(hex(int(tr, 2))[2:])  # Convert to a bytearray
        return to_return

    def execute(self, simulator: M68K):
        """
        Executes this command in a simulator
        :param simulator: The simulator to execute the command on
        :return: Nothing
        """
        # get the length
        val_length = get_number_of_bytes(self.size)

        # get the value of src from the simulator
        src_val = self.src.get_value(simulator, val_length)

        # and set the value
        self.dest.set_value(simulator, src_val, val_length)

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

        >>> Move.is_valid('MOV.L', 'D0, D1')[0]
        False

        >>> Move.is_valid('MOVE.', 'D0, D1')[0]
        False

        :param command: The command itself (e.g. 'MOVE.B', 'LEA', etc.)
        :param parameters: The parameters after the command (such as the source and destination of a move)
        :return: Whether the given command is valid and a list of issues/warnings encountered
        """
        issues = []
        try:
            parts = command.split('.')  # Split the command by period to get the size of the command
            assert len(parts) <= 2, 'Unknown error (more than 1 period in command)'  # If we have more than 2 parts something is seriously wrong
            assert parts[0].upper() == 'MOVE', 'Incorrect command passed in'
            if len(parts) != 1:  # Has a size specifier
                assert len(parts[1]) == 1, 'Size specifier must be 1 character'
                assert parts[1] in Move.allowed_sizes, "Size {} isn't allowed for command {}".format(parts[1], command[0])

            # Split the parameters into EA modes
            params = parameters.split(',')
            assert len(params) == 2, 'Must have two parameters'

            src = parse_assembly_parameter(params[0].strip())  # Parse the source and make sure it parsed right
            assert src, 'Error parsing src'

            dest = parse_assembly_parameter(params[1].strip())
            assert dest, 'Error parsing dest'

            assert src.mode != EAMode.ARD, 'Invalid addressing mode'  # Only invalid src is address register direct
            assert dest.mode != EAMode.ARD and dest.mode != EAMode.IMM, 'Invalid addressing mode'

            return True, issues
        except AssertionError as e:
            issues.append((e.args[0], 'ERROR'))
            return False, issues

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

        >>> Move.get_word_length('MOVE.W', 'D0, ($BBBB).L')
        (3, [])

        >>> Move.get_word_length('MOVE.W', '($AAAA).L, ($BBBB).L')
        (5, [])

        >>> Move.get_word_length('MOVE.W', '#$AAAA, ($BBBB).L')
        (4, [])


        Gets what the end length of this command will be in memory
        :param command: The text of the command itself (e.g. "LEA", "MOVE.B", etc.)
        :param parameters: The parameters after the command
        :return: The length of the bytes in memory in words, as well as a list of warnings or errors encountered
        """
        valid, issues = Move.is_valid(command, parameters)
        if not valid:
            return 0, issues
        # We can forego asserts in here because we've now confirmed this is valid assembly code

        issues = []  # Set up our issues list (warnings + errors)
        parts = command.split('.')  # Split the command by period to get the size of the command
        if len(parts) == 1:  # Use the default size
            size = 'W'
        else:
            size = parts[1]

        # Split the parameters into EA modes
        params = parameters.split(',')

        src = parse_assembly_parameter(params[0].strip())  # Parse the source and make sure it parsed right
        dest = parse_assembly_parameter(params[1].strip())

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

        if dest.mode == EAMode.AWA:  # Appends a word
            length += 1

        if dest.mode == EAMode.ALA:  # Appends a long, so 2 words
            length += 2

        return length, issues


def from_binary(data: bytearray):
    """
    This has a non-move opcode
    >>> from_binary(bytearray.fromhex('5E01'))
    (None, 0)
    
    MOVE.B D1,D7
    >>> op, used = from_binary(bytearray.fromhex('1E01'))
    
    >>> str(op.src)
    'Mode: 0, Data: 1'
    
    >>> str(op.dest)
    'Mode: 0, Data: 7'
    
    >>> used
    1
    
    
    MOVE.L (A4),(A7)
    >>> op, used = from_binary(bytearray.fromhex('2E94'))
    
    >>> str(op.src)
    'Mode: 2, Data: 4'
    
    >>> str(op.dest)
    'Mode: 2, Data: 7'
    
    >>> used
    1
    
    
    MOVE.W #$DEAF,(A2)+
    >>> op, used = from_binary(bytearray.fromhex('34FCDEAF'))
    
    >>> str(op.src)
    'Mode: 5, Data: 57007'
    
    >>> str(op.dest)
    'Mode: 3, Data: 2'
    
    >>> used
    2



    MOVE.L ($1000).W,($200000).L
    >>> op, used = from_binary(bytearray.fromhex('23F8100000200000'))

    >>> str(op.src)
    'Mode: 7, Data: 4096'

    >>> str(op.dest)
    'Mode: 6, Data: 2097152'

    >>> used
    4


    Parses some raw data into an instance of the opcode class
    :param data: The data used to convert into an opcode instance
    :return: The constructed instance or none if there was an error and
        the amount of data in words that was used (e.g. extra for immediate
        data) or 0 for not a match
    """
    assert len(data) >= 2, 'opcode size is at least 1 word'
    
    # 'big' endian byte order
    first_word = int.from_bytes(data[0:2], 'big')
    
    [opcode_bin,
    size_bin,
    destination_register_bin,
    destination_mode_bin,
    source_mode_bin,
    source_register_bin] = split_bits(first_word, [2, 2, 3, 3, 3, 3])
    
    # check opcode
    if opcode_bin != 0b00:
        return (None, 0)
    
    # check size
    if not size_bin in Move.allowed_sizes_binary:
        return (None, 0)
    
    size = MoveSize.parse_binary(size_bin)
    
    wordsUsed = 1
    
    src_EA = parse_ea_from_binary(source_mode_bin, source_register_bin, size, True, data[wordsUsed*2:])
    wordsUsed += src_EA[1]
    
    dest_EA = parse_ea_from_binary(destination_mode_bin, destination_register_bin, size, False, data[wordsUsed*2:])
    wordsUsed += dest_EA[1]
    
    return (Move(src_EA[0], dest_EA[0], size), wordsUsed)
