from ..ea_mode import EAMode
from ..assembly_parameter import AssemblyParameter
from ..ea_mode_bin import parse_ea_from_binary
from ..m68k import M68K
from .opcode import Opcode
from ..op_size import OpSize
from ..parsing import parse_assembly_parameter
from ..split_bits import split_bits
from ..opcode_util import check_valid_command, n_param_is_valid, n_param_from_str, command_matches


class Lea(Opcode):
    pass


class Lea(Opcode):
    """
    LEA: Load Effective Address

    Operation: < ea > → An

    Syntax: LEA < ea > ,An

    Attributes: Size = (Long)

    Description: Loads the effective address into the specified address register. 
    All 32 bits of the address register are effected by this instruction.

    Condition Codes: Not affected.
    """
    
    def __init__(self, params: list):
        assert len(params) == 2
        assert isinstance(params[0], AssemblyParameter)
        assert isinstance(params[1], AssemblyParameter)
        # Can't take data register, address register, or ARI with modifications
        assert params[0].mode not in [EAMode.DRD, EAMode.ARD, EAMode.ARIPD, EAMode.ARIPI, EAMode.IMM]
        self.src = params[0]

        # Check that the destination is of a proper type
        assert params[1].mode == EAMode.ARD  # Can only take address register direct
        self.dest = params[1]

    def assemble(self) -> bytearray:
        """
        Assembles this opcode into hex to be inserted into memory
        :return: The hex version of this opcode
        """
        # create the opcode
        ret_opcode = 0b0100 << 12
        ret_opcode |= self.dest.data << 9
        ret_opcode |= 0b111 << 6
        ret_opcode |= ea_mode_bin.parse_from_ea_mode_modefirst(self.src)

        ret_bytes = bytearray(ret_opcode.to_bytes(2, byteorder='big', signed=False))

        ret_bytes.extend(
            ea_to_binary_post_op(self.src,
                                             OpSize.LONG if self.src.mode == EAMode.ALA else OpSize.WORD)
        .get_value_bytearray())

        return ret_bytes

    def execute(self, simulator: M68K):
        """
        Executes this command in a simulator
        :param simulator: The simulator to execute the command on
        :return: Nothing
        """

        val_len = OpSize.LONG.get_number_of_bytes()

        # get the value of the source
        src_val = self.src.get_value(simulator, val_len)

        # set the value in the dest
        self.dest.set_value(simulator, src_val)

        # increment the program counter by at least 2 bytes (1 word)
        to_increment = 2

        if self.src.mode is EAMode.AddressRegisterIndirect:
            to_increment += val_len

        if self.src.mode is EAMode.AbsoluteWordAddress:
            to_increment += OpSize.LONG.value

        if self.src.mode is EAMode.AbsoluteLongAddress:
            to_increment += OpSize.LONG.value

        simulator.increment_program_counter(to_increment)


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
        return command_matches(command, 'LEA')

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
            return 0

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
        return n_param_is_valid(command, parameters, "LEA", 2, None, None,
                                            [[EAMode.DRD, EAMode.ARD, EAMode.ARIPD, EAMode.ARIPI],
                                             [mode for mode in EAMode if mode is not EAMode.ARD]])  # Select all but ARD

    @classmethod
    def disassemble_instruction(cls, data: bytearray) -> (Lea, int):
        """
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
         register_bin,
         ones_bin,
         ea_mode,
         ea_reg] = split_bits(first_word, [4, 3, 3, 3, 3])

        # check opcode
        if opcode_bin != 0b0100 or ones_bin != 0b111:  # Second condition to distinguish from TRAP
            return None

        wordsUsed = 1

        src_EA = parse_ea_from_binary(ea_mode, ea_reg, OpSize.LONG, True, data[wordsUsed * 2:])
        wordsUsed += src_EA[1]

        dest_EA = AssemblyParameter(EAMode.ARD, register_bin)

        # when making the new Move, need to convert that MoveSize back into an OpSize
        return cls([src_EA[0], dest_EA])

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
        return n_param_from_str(command, parameters, Lea, 2, None)
