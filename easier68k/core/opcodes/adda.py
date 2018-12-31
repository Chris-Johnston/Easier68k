from ...core.enum.ea_mode import EAMode
from ...core.enum import ea_mode_bin
from ...core.opcodes.opcode import Opcode
from ...simulator.m68k import M68K
from ...core.enum.ea_mode_bin import parse_ea_from_binary
from ...core.models.assembly_parameter import AssemblyParameter
from ...core.util import opcode_util
from ..util.parsing import parse_assembly_parameter
from ...core.enum.op_size import OpSize
from ..util.split_bits import split_bits
from ..models.memory_value import MemoryValue

class Adda(Opcode):
    pass

class Adda(Opcode):
    """
    ADDA  Add Address  ADDA
    Operation: Source + Destination → Destination
    Syntax: ADDA < ea > , An
    Attributes: Size = (Word, Long)

    Description: Adds the source operand to the destination address register and stores the
    result in the address register. The size of the operation may be specified as word or
    long. The entire destination address register is used regardless of the operation size.

    Condition Codes: Not affected

    Instruction Fields: Register field—Specifies any of the eight address registers. This is always the
    destination. Opmode field—Specifies the size of the operation.
    011— Word operation; the source operand is sign-extended to a long operand and
    the operation is performed on the address register using all 32 bits.
    111— Long operation.
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
        assert size in Adda.valid_sizes

        self.size = size

    def assemble(self) -> bytearray:
        """
        Assembles this opcode into hex to be inserted into memory
        :return: The hex version of this opcode
        """
        # create the opcode
        ret_opcode = 0b1101 << 12
        ret_opcode |= self.dest.data << 9
        ret_opcode |= (0b011 if self.size == OpSize.WORD else 0b111) << 6
        ret_opcode |= ea_mode_bin.parse_from_ea_mode_modefirst(self.src) << 0

        ret_bytes = bytearray(ret_opcode.to_bytes(2, byteorder='big', signed=False))

        if self.src.mode == EAMode.IMM or self.src.mode == EAMode.AWA or self.src.mode == EAMode.ALA:
            ret_bytes.extend(opcode_util.ea_to_binary_post_op(self.src, self.size).get_value_bytearray())

        return ret_bytes

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

        # get the value of dest from the simulator
        dest_val = self.dest.get_value(simulator, val_length)

        # increment the program counter by the length of the instruction (1 word)
        to_increment = OpSize.WORD.value

        if self.src.mode in [EAMode.Immediate]:
            # add the length of the size of the operation, in words
            to_increment += self.size.value

        # if followed by a long addr, add the length of the long
        if self.src.mode in [EAMode.AbsoluteLongAddress]:
            to_increment += OpSize.LONG.value

        # same goes with a word
        if self.src.mode in [EAMode.AbsoluteWordAddress]:
            to_increment += OpSize.WORD.value

        # mask to apply to the complement
        mask = (0xFFFF0000 if self.size == OpSize.WORD else 0xFFFFFFFF)

        # Calculate the total
        total = src_val + dest_val

        raw_total = total.get_value_unsigned()

        # Logic should go here to take the proper two's complement of the
        if src_val.get_value_signed() < 0:
            raw_total = raw_total | mask

        # set the value
        self.dest.set_value(simulator, MemoryValue(OpSize.LONG, unsigned_int=raw_total))

        # set the program counter value
        simulator.increment_program_counter(to_increment)

    def __str__(self):
        # Makes this a bit easier to read in doctest output
        return 'Adda command: Size {}, src {}, dest {}'.format(self.size, self.src, self.dest)

    @classmethod
    def command_matches(cls, command: str) -> bool:
        """
        Checks whether a command string is an instance of this command type
        :param command: The command string to check (e.g. 'MOVE.B', 'LEA', etc.)
        :return: Whether the string is an instance of this command type
        """
        return opcode_util.command_matches(command, 'ADDA')

    @classmethod
    def get_word_length(cls, command: str, parameters: str) -> int:
        """
        >>> Adda.get_word_length('ADDA.W', 'D0, A1')
        1

        >>> Adda.get_word_length('ADDA.W', '#$90, A0')
        2

        >>> Adda.get_word_length('ADDA.L', '#$90, A3')
        3

        >>> Adda.get_word_length('ADDA.W', '#$90, A3')
        2

        >>> Adda.get_word_length('ADDA.W', '(A0), A1')
        1

        >>> Adda.get_word_length('ADDA.W', '#$ABCDE, A0')
        2

        >>> Adda.get_word_length('ADDA.L', '($AAAA).L, A6')
        3

        >>> Adda.get_word_length('ADDA.W', '($AAAA).W, A5')
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

        src = parse_assembly_parameter(params[0].strip())  # Parse the source and make sure it parsed right
        # dest = parse_assembly_parameter(params[1].strip())

        length = 1  # Always 1 word not counting additions to end

        if src.mode == EAMode.IMM:  # If we're moving an immediate we have to append the value afterwards
            if size == OpSize.LONG:
                length += 2
            else:
                length += 1

        if src.mode == EAMode.AWA:  # Appends a word
            length += 1

        if src.mode == EAMode.ALA:  # Appends a long, so 2 words
            length += 2

        return length

    @classmethod
    def is_valid(cls, command: str, parameters: str) -> (bool, list):
        """
        Tests whether the given command is valid

        >>> Adda.is_valid('ADDA', '(A0), A1')[0]
        True

        >>> Adda.is_valid('ADDA.W', '(A0)+')[0]
        False

        >>> Adda.is_valid('ADDA.B', '(A0), A1')[0]
        False

        >>> Adda.is_valid('ADDA.W', 'D0, A2')[0]
        True

        >>> Adda.is_valid('ADDA.L', '#$0A, A4')[0]
        True

        >>> Adda.is_valid('ADDA.L', '($AAAA).L, A7')[0]
        True

        :param command: The command itself (e.g. 'MOVE.B', 'LEA', etc.)
        :param parameters: The parameters after the command (such as the source and destination of a move)
        :return: Whether the given command is valid and a list of issues/warnings encountered
        """
        return opcode_util.n_param_is_valid(command, parameters, "ADDA", 2, Adda.valid_sizes)

    @classmethod
    def disassemble_instruction(cls, data: bytearray) -> (Adda, int):
        """
        This has a non-adda opcode
        >>> Adda.disassemble_instruction(bytearray.fromhex('1E00'))


        ADDA.W A1,A7
        >>> op = Adda.disassemble_instruction(bytearray.fromhex('DEC9'))

        >>> str(op.src)
        'EA Mode: EAMode.ARD, Data: 1'

        >>> str(op.dest)
        'EA Mode: EAMode.ARD, Data: 7'


        ADDA.W #0, A1
        >>> op = Adda.disassemble_instruction(bytearray.fromhex('D2FC0000'))

        >>> str(op.src)
        'EA Mode: EAMode.IMM, Data: 0'

        >>> str(op.dest)
        'EA Mode: EAMode.ARD, Data: 1'


        ADDA.W D3, A0
        >>> op = Adda.disassemble_instruction(bytearray.fromhex('D0C3'))

        >>> str(op.src)
        'EA Mode: EAMode.DRD, Data: 3'

        >>> str(op.dest)
        'EA Mode: EAMode.ARD, Data: 0'


        ADDA.W ($0A0B).W, A6
        >>> op = Adda.disassemble_instruction(bytearray.fromhex('DCF80A0B'))

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
         register_bin,
         opmode_bin,
         ea_mode,
         ea_reg] = split_bits(first_word, [4, 3, 3, 3, 3])

        # check opcode (and size)
        if opcode_bin != 0b1101 or opmode_bin != 0b011 and opmode_bin != 0b111:
            return None

        wordsUsed = 1

        size = OpSize.WORD if opmode_bin == 0b0011 else OpSize.LONG

        src_EA = parse_ea_from_binary(ea_mode, ea_reg, size, True, data[wordsUsed * 2:])
        wordsUsed += src_EA[1]

        dest_EA = AssemblyParameter(EAMode.ARD, register_bin)

        # when making the new Move, need to convert that MoveSize back into an OpSize
        return cls((src_EA[0], dest_EA), size)

    @classmethod
    def from_str(cls, command: str, parameters: str):
        """
        Parses a ADDA command from text.

        >>> str(Adda.from_str('ADDA.W', 'A5, A3'))
        'Adda command: Size OpSize.WORD, src EA Mode: EAMode.ARD, Data: 5, dest EA Mode: EAMode.ARD, Data: 3'

        >>> str(Adda.from_str('ADDA.L', '(A0)+, A4'))
        'Adda command: Size OpSize.LONG, src EA Mode: EAMode.ARIPI, Data: 0, dest EA Mode: EAMode.ARD, Data: 4'

        :param command: The command itself (e.g. 'MOVE.B', 'LEA', etc.)
        :param parameters: The parameters after the command (such as the source and destination of a move)
        :return: The parsed command
        """
        return opcode_util.n_param_from_str(command, parameters, Adda, 2, OpSize.WORD)
