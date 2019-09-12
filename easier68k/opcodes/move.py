from ..ea_mode import EAMode
from ..op_size import MoveSize, OpSize
from ..ea_mode_bin import parse_ea_from_binary, parse_from_ea_mode_regfirst, parse_from_ea_mode_modefirst
from ..m68k import M68K
from .opcode import Opcode
from ..split_bits import split_bits
from ..parsing import parse_assembly_parameter, from_str_util
from ..assembly_parameter import AssemblyParameter
from ..opcode_util import check_valid_command, n_param_is_valid, n_param_from_str, command_matches, ea_to_binary_post_op


class Move(Opcode):  # Forward declaration
    pass


class Move(Opcode):
    """
    MOVE: Move Data from Source to Destination

    Operation: Source → Destination

    Syntax: MOVE < ea > , < ea >

    Attributes: Size = (Byte, Word, Long)

    Description: Moves the data at the source to the destination location and sets the 
    condition codes according to the data. The size of the operation may be specified as 
    byte, word, or long. 

    Condition Codes:
    X — Not affected.
    N — Set if the result is negative; cleared otherwise.
    Z — Set if the result is zero; cleared otherwise.
    V — Always cleared.
    C — Always cleared.

    Size field: Specifies the size of the operand to be moved.
    01 — Byte operation
    11 — Word operation
    10 — Long operation

    Source Effective Address field—Specifies the source operand. All addressing modes
    can be used as listed in the following tables:

    NOTE: Most assemblers use MOVEA when the destination is an
    address register. MOVEQ can be used to move an immediate 8-bit value to a data
    register.
    """

    # Allowed sizes for this opcode
    valid_sizes = [OpSize.BYTE, OpSize.WORD, OpSize.LONG]

    def __init__(self, params: list, size: OpSize = OpSize.WORD):
        assert len(params) == 2
        assert isinstance(params[0], AssemblyParameter)
        assert isinstance(params[1], AssemblyParameter)
        # Check that the src is of the proper type (for example, can't move from an address register for a move command)
        assert params[0].mode != EAMode.ARD  # Only invalid src is address register direct
        self.src = params[0]

        # Check that the destination is of a proper type
        assert params[1].mode != EAMode.ARD and params[
            1].mode != EAMode.IMM  # Can't take address register direct or immediates
        self.dest = params[1]

        # Check that this is a valid size (for example, 'MOVEA.B' is not a valid command)
        assert size in Move.valid_sizes

        self.size = size

    def assemble(self) -> bytearray:
        """
        Assembles this opcode into hex to be inserted into memory
        :return: The hex version of this opcode
        """
        # 00 <size> <dest reg> <dest mode> <src mode> <src reg>

        ret_opcode = 0
        # can ignore the zero MSB
        # ret_opcode = 00 << 13

        # add the size
        ret_opcode |= MoveSize.from_op_size(self.size) << 12

        # add the destination reg and dest mode
        ret_opcode |= parse_from_ea_mode_regfirst(self.dest) << 6

        # add the src mode and src reg
        ret_opcode |= parse_from_ea_mode_modefirst(self.src)

        # convert the opcode word to bytes
        ret_bytes = bytearray(ret_opcode.to_bytes(2, byteorder='big', signed=False))

        # append the immediates / absolute addresses after the command opcode
        # this data can be done if the value is not an immediate or absolute addr
        data_to_append = (ea_to_binary_post_op(self.src, self.size),
                          ea_to_binary_post_op(self.dest, self.size))
        for data in data_to_append:
            if data is not None:
                ret_bytes.extend(data.get_value_bytearray())

        return ret_bytes

    def execute(self, simulator: M68K):
        """
        Executes this command in a simulator
        :param simulator: The simulator to execute the command on
        :return: Nothing
        """
        # get the value of src from the simulator
        src_val = self.src.get_value(simulator, self.size)

        # and set the value
        self.dest.set_value(simulator, src_val)

        # increment the program counter by the length of the instruction (1 word)
        to_increment = OpSize.WORD.value

        if self.src.mode in [EAMode.Immediate]:
            # add the length of the size of the operation, in words
            if self.size is OpSize.BYTE:
                to_increment += OpSize.WORD.value
            else:
                to_increment += self.size.value

        # if followed by a long addr, add the length of the long
        if self.src.mode in [EAMode.AbsoluteLongAddress]:
            to_increment += OpSize.LONG.value

        # same goes with a word
        if self.src.mode in [EAMode.AbsoluteWordAddress]:
            to_increment += OpSize.WORD.value

        # repeat for the dest
        if self.dest.mode in [EAMode.AbsoluteLongAddress]:
            to_increment += OpSize.LONG.value

        if self.dest.mode in [EAMode.AbsoluteWordAddress]:
            to_increment += OpSize.WORD.value

        # get the current program counter
        pc_val = simulator.get_program_counter_value()

        # set the program counter value
        simulator.increment_program_counter(to_increment)

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
        return command_matches(command, 'MOVE')

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
        return n_param_is_valid(command, parameters, "MOVE", 2, param_invalid_modes=[[EAMode.ARD],
                                                                                                 [EAMode.ARD,
                                                                                                  EAMode.IMM]])

    @classmethod
    def disassemble_instruction(cls, data: bytearray) -> Opcode:
        """
        This has a non-move opcode
        >>> Move.disassemble_instruction(bytearray.fromhex('5E01'))


        MOVE.B D1,D7
        >>> op = Move.disassemble_instruction(bytearray.fromhex('1E01'))

        >>> str(op.src)
        'EA Mode: EAMode.DRD, Data: 1'

        >>> str(op.dest)
        'EA Mode: EAMode.DRD, Data: 7'


        MOVE.L (A4),(A7)
        >>> op = Move.disassemble_instruction(bytearray.fromhex('2E94'))

        >>> str(op.src)
        'EA Mode: EAMode.ARI, Data: 4'

        >>> str(op.dest)
        'EA Mode: EAMode.ARI, Data: 7'

        MOVE.W #$DEAF,(A2)+
        >>> op = Move.disassemble_instruction(bytearray.fromhex('34FCDEAF'))

        >>> str(op.src)
        'EA Mode: EAMode.IMM, Data: 57007'

        >>> str(op.dest)
        'EA Mode: EAMode.ARIPI, Data: 2'

        MOVE.L ($1000).W,($200000).L
        >>> op = Move.disassemble_instruction(bytearray.fromhex('23F8100000200000'))

        >>> str(op.src)
        'EA Mode: EAMode.AWA, Data: 4096'

        >>> str(op.dest)
        'EA Mode: EAMode.ALA, Data: 2097152'

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
            return None

        # the binary will contain the MoveSize, convert this to an OpSize used by everything else
        size = MoveSize(size_bin).to_op_size()

        # check size
        if size not in Move.valid_sizes:
            return None

        wordsUsed = 1

        src_EA = parse_ea_from_binary(source_mode_bin, source_register_bin, size, True, data[wordsUsed * 2:])
        wordsUsed += src_EA[1]

        dest_EA = parse_ea_from_binary(destination_mode_bin, destination_register_bin, size, False,
                                       data[wordsUsed * 2:])

        # when making the new Move, need to convert that MoveSize back into an OpSize
        return cls((src_EA[0], dest_EA[0]), size)

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
        return n_param_from_str(command, parameters, Move, 2, OpSize.WORD)
