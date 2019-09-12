from ..ea_mode import EAMode
from .opcode import Opcode
from ..m68k import M68K
from ..ea_mode_bin import parse_ea_from_binary, parse_from_ea_mode_modefirst
from ..assembly_parameter import AssemblyParameter
from ..parsing import parse_assembly_parameter
from ..op_size import OpSize
from ..split_bits import split_bits
from ..opcode_util import check_valid_command, n_param_is_valid, n_param_from_str, command_matches, ea_to_binary_post_op


class Movea(Opcode):
    """
    MOVEA: Move Address
    Operation: Source -> Destination
    Assembler Syntax: MOVEA <ea>, An
    Attributes: Size = (Word, Long)
    Description: Moves the contents of the source to the destination address register.
                 The size of the operation is specified as word or long.
                 Word-size source operands are sign-extended to 32-bit quantities.
    Condition Codes: Not affected
    Instruction Format: 00 Signature xx Size xxx DestRegister 001 Const xxx EAMode xxx EARegister
    Instruction Fields:
        Size field - Specifies the size of the operation.
            11 - Word operation
            10 - Long operation

        Destination Register field- specifies the destination address register.

        Effective Address field - Specifies the location of the source operand.
                                  All addressing modes can be used.
            Valid Modes - All
    """

    # Allowed sizes for this opcode
    valid_sizes = [OpSize.WORD, OpSize.LONG]

    def __init__(self, params: list, size: OpSize = OpSize.WORD):
        assert len(params) == 2
        assert isinstance(params[0], AssemblyParameter)
        assert isinstance(params[1], AssemblyParameter)

        self.src = params[0]

        # Check that the destination is of a proper type
        assert params[1].mode == EAMode.ARD  # Can only take address register direct
        self.dest = params[1]

        # Check that this is a valid size (for example, 'ADDA.B' is not a valid command)
        assert size in Movea.valid_sizes

        self.size = size

    def assemble(self) -> bytearray:
        """
        Assembles this opcode into hex to be inserted into memory
        :return: The hex version of this opcode
        """
        # create the opcode
        ret_opcode = 0 << 14
        ret_opcode |= (0b11 if self.size == OpSize.WORD else 0b10) << 12
        ret_opcode |= self.dest.data << 9
        ret_opcode |= 0b001 << 6
        ret_opcode |= parse_from_ea_mode_modefirst(self.src) << 0

        ret_bytes = bytearray(ret_opcode.to_bytes(2, byteorder='big', signed=False))

        src_mode = self.src.mode

        if src_mode == EAMode.IMM or src_mode == EAMode.AWA or src_mode == EAMode.ALA:
            to_extend = ea_to_binary_post_op(self.src, self.size).get_value_bytearray()
            ret_bytes.extend(to_extend)

        return ret_bytes

    def execute(self, simulator: M68K):
        """
        Executes this command in a simulator
        :param simulator: The simulator to execute the command on
        :return: None
        """
        # get the length
        val_length = self.size.get_number_of_bytes()

        # get the value of src from the simulator
        src_val = self.src.get_value(simulator, val_length)

        # set the value of dest from the simulator
        self.dest.set_value(simulator, src_val)

        # increment the program counter by the length of the instruction (1 word)
        to_increment = OpSize.WORD.value

        if self.src.mode in [EAMode.Immediate]:
            # add the length of the size of the operation, in words
            to_increment += self.size.value
        # if followed by a long addr, add the length of the long
        elif self.src.mode in [EAMode.AbsoluteLongAddress]:
            to_increment += OpSize.LONG.value
        # same goes with a word
        elif self.src.mode in [EAMode.AbsoluteWordAddress]:
            to_increment += OpSize.WORD.value

        # set the program counter value
        simulator.increment_program_counter(to_increment)

    def __str__(self):
        # Makes this a bit easier to read in doctest output
        return 'Movea command: Size {}, src {}, dest {}'.format(self.size, self.src, self.dest)

    @classmethod
    def command_matches(cls, command: str) -> bool:
        """
        Checks whether a command string is an instance of this command type
        :param command: The command string to check (e.g. 'MOVE.B', 'LEA', etc.)
        :return: Whether the string is an instance of this command type
        """
        return command_matches(command, 'ADDA')

    @classmethod
    def get_word_length(cls, command: str, parameters: str) -> int:
        """
        >>> Movea.get_word_length('MOVEA.W', 'D0, A1')
        1

        >>> Movea.get_word_length('MOVEA.W', '#$90, A0')
        2

        >>> Movea.get_word_length('MOVEA.L', '#$90, A3')
        3

        >>> Movea.get_word_length('MOVEA.W', '#$90, A3')
        2

        >>> Movea.get_word_length('MOVEA.W', '(A0), A1')
        1

        >>> Movea.get_word_length('MOVEA.W', '#$ABCDE, A0')
        2

        >>> Movea.get_word_length('MOVEA.L', '($AAAA).L, A6')
        3

        >>> Movea.get_word_length('MOVEA.W', '($AAAA).W, A5')
        2

        Gets what the end length of this command will be in memory
        :param command: The text of the command itself (e.g. "LEA", "MOVE.B", etc.)
        :param parameters: The parameters after the command
        :return: The length of the bytes in memory in words,
                 as well as a list of warnings or errors encountered
        """
        valid, issues = cls.is_valid(command, parameters)
        if not valid:
            return 0
        # We can forego asserts in here because we've now confirmed this is valid assembly code

        parts = command.split('.')  # Split the command by period to get the size of the command
        if len(parts) == 1:  # Use the default size
            size = OpSize.WORD
        else:
            size = OpSize.parse(parts[1])

        # Split the parameters into EA modes
        params = parameters.split(',')

        if len(params) != 2:  # We need exactly 2 parameters
            issues.append(('Invalid syntax (missing a parameter/too many parameters)', 'ERROR'))
            return 0

        # Parse the source and make sure it parsed right
        src = parse_assembly_parameter(params[0].strip())

        length = 1  # Always 1 word not counting additions to end

        # If we're moving an immediate we have to append the value afterwards
        if src.mode == EAMode.IMM:
            if size == OpSize.LONG:
                length += 2
            else:
                length += 1
        elif src.mode == EAMode.AWA:  # Appends a word
            length += 1
        elif src.mode == EAMode.ALA:  # Appends a long, so 2 words
            length += 2

        return length

    @classmethod
    def is_valid(cls, command: str, parameters: str) -> (bool, list):
        """
        Tests whether the given command is valid

        >>> Movea.is_valid('MOVEA', '(A0), A1')[0]
        True

        >>> Movea.is_valid('MOVEA.W', '(A0)+')[0]
        False

        >>> Movea.is_valid('MOVE.B', '(A0), A1')[0]
        False

        >>> Movea.is_valid('MOVEA.W', 'D0, A2')[0]
        True

        >>> Movea.is_valid('MOVEA.L', '#$0A, A4')[0]
        True

        >>> Movea.is_valid('MOVEA.L', '($AAAA).L, A7')[0]
        True

        :param command: The command itself (e.g. 'MOVE.B', 'LEA', etc.)
        :param parameters: The parameters after the command
                           (such as the source and destination of a move)
        :return: Whether the given command is valid and a list of issues/warnings encountered
        """
        return n_param_is_valid(command, parameters, "MOVEA", 2, Movea.valid_sizes)

    @classmethod
    def disassemble_instruction(cls, data: bytearray) -> Opcode:
        """
        This has a non-movea opcode
        >>> Movea.disassemble_instruction(bytearray.fromhex('1E00'))


        MOVEA.W A1,A7
        >>> op = Movea.disassemble_instruction(bytearray.fromhex('3E49'))

        >>> str(op.src)
        'EA Mode: EAMode.ARD, Data: 1'

        >>> str(op.dest)
        'EA Mode: EAMode.ARD, Data: 7'


        MOVEA.W #0, A1
        >>> op = Movea.disassemble_instruction(bytearray.fromhex('327C0000'))

        >>> str(op.src)
        'EA Mode: EAMode.IMM, Data: 0'

        >>> str(op.dest)
        'EA Mode: EAMode.ARD, Data: 1'


        MOVEA.W D3, A0
        >>> op = Movea.disassemble_instruction(bytearray.fromhex('3043'))

        >>> str(op.src)
        'EA Mode: EAMode.DRD, Data: 3'

        >>> str(op.dest)
        'EA Mode: EAMode.ARD, Data: 0'


        MOVEA.W ($0A0B).W, A6
        >>> op = Movea.disassemble_instruction(bytearray.fromhex('3C780A0B'))

        >>> str(op.src)
        'EA Mode: EAMode.AWA, Data: 2571'

        >>> str(op.dest)
        'EA Mode: EAMode.ARD, Data: 6'

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
         register_bin,
         const_bin,
         ea_mode,
         ea_reg] = split_bits(first_word, [2, 2, 3, 3, 3, 3])

        # check opcode, size, and constant
        if opcode_bin != 0b00 or (size_bin != 0b11 and size_bin != 0b10) or const_bin != 0b001:
            return None

        size = OpSize.WORD if size_bin == 0b11 else OpSize.LONG

        src_ea = parse_ea_from_binary(ea_mode, ea_reg, size, True, data[OpSize.WORD.value:])

        dest_ea = AssemblyParameter(EAMode.ARD, register_bin)

        # when making the new Move, need to convert that MoveSize back into an OpSize
        return cls([src_ea[0], dest_ea], size)

    @classmethod
    def from_str(cls, command: str, parameters: str):
        """
        Parses a MOVEA command from text.

        >>> str(Movea.from_str('MOVEA.W', 'A5, A3'))
        'Movea command: Size OpSize.WORD, src EA Mode: EAMode.ARD, Data: 5, dest EA Mode: EAMode.ARD, Data: 3'

        >>> str(Movea.from_str('MOVEA.L', '(A0)+, A4'))
        'Movea command: Size OpSize.LONG, src EA Mode: EAMode.ARIPI, Data: 0, dest EA Mode: EAMode.ARD, Data: 4'

        :param command: The command itself (e.g. 'MOVE.B', 'LEA', etc.)
        :param parameters: The parameters after the command
                           (such as the source and destination of a move)
        :return: The parsed command
        """
        return n_param_from_str(command, parameters, Movea, 2, OpSize.WORD)
