from ...core.enum.ea_mode import EAMode
from ...core.enum.op_size import MoveSize, OpSize
from ...core.enum import ea_mode_bin
from ...core.enum.ea_mode_bin import parse_ea_from_binary
from ...simulator.m68k import M68K
from ...core.opcodes.opcode import Opcode
from ...core.util.split_bits import split_bits
from ...core.util import opcode_util
from ..util.parsing import parse_assembly_parameter, from_str_util
from ..models.assembly_parameter import AssemblyParameter


class Move(Opcode):  # Forward declaration
    pass


class Move(Opcode):

    # Allowed sizes for this opcode
    valid_sizes = [OpSize.BYTE, OpSize.WORD, OpSize.LONG]

    def __init__(self, src: AssemblyParameter, dest: AssemblyParameter, size: OpSize = OpSize.WORD):
        assert isinstance(src, AssemblyParameter)
        assert isinstance(dest, AssemblyParameter)
        # Check that the src is of the proper type (for example, can't move from an address register for a move command)
        assert src.mode != EAMode.ARD  # Only invalid src is address register direct
        self.src = src

        # Check that the destination is of a proper type
        assert dest.mode != EAMode.ARD and dest.mode != EAMode.IMM  # Can't take address register direct or immediates
        self.dest = dest

        # Check that this is a valid size (for example, 'MOVEA.B' is not a valid command)

        assert size in Move.valid_sizes

        self.size = size

    def assemble(self) -> bytearray:
        """
        Assembles this opcode into hex to be inserted into memory
        :return: The hex version of this opcode
        """
        # Create a binary string to append to, which we'll convert to hex at the end
        tr = '00'  # Opcode
        tr += '{0:02b}'.format(MoveSize.from_op_size(self.size))  # Size bits
        tr += ea_mode_bin.parse_from_ea_mode_regfirst(self.dest)  # Destination first
        tr += ea_mode_bin.parse_from_ea_mode_modefirst(self.src)  # Source second
        # Append immediates/absolute addresses after the command
        tr += opcode_util.ea_to_binary_post_op(self.src, self.size)
        tr += opcode_util.ea_to_binary_post_op(self.dest, self.size)

        to_return = bytearray.fromhex(hex(int(tr, 2))[2:])  # Convert to a bytearray
        return to_return

    def execute(self, simulator: M68K):
        """
        Executes this command in a simulator
        :param simulator: The simulator to execute the command on
        :return: Nothing
        """
        # get the length
        val_length = self.size.get_number_of_bytes()

        # get the value of src from the simulator
        src_val = self.src.get_value(simulator, val_length)

        # and set the value
        self.dest.set_value(simulator, src_val, val_length)

    def __str__(self):
        # Makes this a bit easier to read in doctest output
        return 'Move command: Size {}, src {}, dest {}'.format(self.size, self.src, self.dest)

    @classmethod
    def command_matches(cls, command: str) -> bool:
        """
        Checks whether a command string is an instance of this command type
        :param command: The command string to check (e.g. 'MOVE.B', 'LEA', etc.)
        :return: Whether the string is an instance of this command type
        """
        return opcode_util.command_matches(command, 'MOVE')

    @classmethod
    def get_word_length(cls, command: str, parameters: str) -> int:
        """
        >>> Move.get_word_length('MOVE', 'D0, D1')
        1

        >>> Move.get_word_length('MOVE.L', '#$90, D3')
        3

        >>> Move.get_word_length('MOVE.W', '#$90, D3')
        2

        >>> Move.get_word_length('MOVE.W', '($AAAA).L, D7')
        3

        >>> Move.get_word_length('MOVE.W', 'D0, ($BBBB).L')
        3

        >>> Move.get_word_length('MOVE.W', '($AAAA).L, ($BBBB).L')
        5

        >>> Move.get_word_length('MOVE.W', '#$AAAA, ($BBBB).L')
        4


        Gets what the end length of this command will be in memory
        :param command: The text of the command itself (e.g. "LEA", "MOVE.B", etc.)
        :param parameters: The parameters after the command
        :return: The length of the bytes in memory in words, as well as a list of warnings or errors encountered
        """
        valid, issues = cls.is_valid(command, parameters)
        if not valid:
            return None
        # We can forego asserts in here because we've now confirmed this is valid assembly code

        issues = []  # Set up our issues list (warnings + errors)
        parts = command.split('.')  # Split the command by period to get the size of the command
        if len(parts) == 1:  # Use the default size
            size = OpSize.WORD
        else:
            size = OpSize.parse(parts[1])

        # Split the parameters into EA modes
        params = parameters.split(',')

        src = parse_assembly_parameter(params[0].strip())  # Parse the source and make sure it parsed right
        dest = parse_assembly_parameter(params[1].strip())

        length = 1  # Always 1 word not counting additions to end

        if src.mode == EAMode.IMM:  # If we're moving an immediate we have to append the value afterwards
            if size == OpSize.LONG:
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

        return length

    @classmethod
    def is_valid(cls, command: str, parameters: str) -> (bool, list):
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
        return opcode_util.two_param_is_valid(command, parameters, "MOVE", param1_invalid_modes=[EAMode.ARD],
                                              param2_invalid_modes=[EAMode.ARD, EAMode.IMM])

    @classmethod
    def from_binary(cls, data: bytearray) -> (Move, int):
        """
        This has a non-move opcode
        >>> Move.from_binary(bytearray.fromhex('5E01'))
        (None, 0)

        MOVE.B D1,D7
        >>> op, used = Move.from_binary(bytearray.fromhex('1E01'))

        >>> str(op.src)
        'EA Mode: EAMode.DRD, Data: 1'

        >>> str(op.dest)
        'EA Mode: EAMode.DRD, Data: 7'

        >>> used
        1


        MOVE.L (A4),(A7)
        >>> op, used = Move.from_binary(bytearray.fromhex('2E94'))

        >>> str(op.src)
        'EA Mode: EAMode.ARI, Data: 4'

        >>> str(op.dest)
        'EA Mode: EAMode.ARI, Data: 7'

        >>> used
        1


        MOVE.W #$DEAF,(A2)+
        >>> op, used = Move.from_binary(bytearray.fromhex('34FCDEAF'))

        >>> str(op.src)
        'EA Mode: EAMode.IMM, Data: 57007'

        >>> str(op.dest)
        'EA Mode: EAMode.ARIPI, Data: 2'

        >>> used
        2



        MOVE.L ($1000).W,($200000).L
        >>> op, used = Move.from_binary(bytearray.fromhex('23F8100000200000'))

        >>> str(op.src)
        'EA Mode: EAMode.AWA, Data: 4096'

        >>> str(op.dest)
        'EA Mode: EAMode.ALA, Data: 2097152'

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

        # the binary will contain the MoveSize, convert this to an OpSize used by everything else
        size = MoveSize(size_bin).to_op_size()

        # check size
        if size not in Move.valid_sizes:
            print('size not in valid', size)
            return (None, 0)

        wordsUsed = 1

        src_EA = parse_ea_from_binary(source_mode_bin, source_register_bin, size, True, data[wordsUsed*2:])
        wordsUsed += src_EA[1]

        dest_EA = parse_ea_from_binary(destination_mode_bin, destination_register_bin, size, False, data[wordsUsed*2:])
        wordsUsed += dest_EA[1]

        # when making the new Move, need to convert that MoveSize back into an OpSize

        return cls(src_EA[0], dest_EA[0], size), wordsUsed

    @classmethod
    def from_str(cls, command: str, parameters: str):
        """
        Parses a MOVE command from text.

        >>> str(Move.from_str('MOVE.B', '-(A0), D1'))
        'Move command: Size OpSize.BYTE, src EA Mode: EAMode.ARIPD, Data: 0, dest EA Mode: EAMode.DRD, Data: 1'

        >>> str(Move.from_str('MOVE.L', 'D3, (A0)'))
        'Move command: Size OpSize.LONG, src EA Mode: EAMode.DRD, Data: 3, dest EA Mode: EAMode.ARI, Data: 0'

        :param command: The command itself (e.g. 'MOVE.B', 'LEA', etc.)
        :param parameters: The parameters after the command (such as the source and destination of a move)
        :return: The parsed command
        """
        return opcode_util.two_param_from_str(command, parameters, Move, OpSize.WORD)
