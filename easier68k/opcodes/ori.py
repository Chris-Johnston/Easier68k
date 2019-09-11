from ..ea_mode import EAMode
from ..assembly_parameter import AssemblyParameter
from ..ea_mode_bin import parse_ea_from_binary
from ..m68k import M68K
from ..split_bits import split_bits
from .opcode import Opcode
from ..op_size import OpSize
from ..parsing import parse_assembly_parameter
from ..condition_status_code import ConditionStatusCode
from ..memory_value import MemoryValue


class Ori(Opcode):  # Forward declaration
    pass


class Ori(Opcode):
    """
    ORI: Inclusive-OR

    Operation: Immediate Data V Destination → Destination

    Syntax: ORI # < data > , < ea >

    Attributes: Size = (Byte, Word, Long)
    
    Description: Performs an inclusive-OR operation on the immediate data and the
    destination operand and stores the result in the destination location. The size of the
    operation is specified as byte, word, or long. The size of the immediate data matches
    the operation size.

    Condition Codes:
    X — Not affected.
    N — Set if the most significant bit of the result is set; cleared otherwise.
    Z — Set if the result is zero; cleared otherwise.
    V — Always cleared.
    C — Always cleared.

    Size field—Specifies the size of the operation.
    00— Byte operation
    01— Word operation
    10— Long operation

    Immediate field: —Data immediately following the instruction.
    If size = 00, the data is the low-order byte of the immediate word.
    If size = 01, the data is the entire immediate word.
    If size = 10, the data is the next two immediate words.
    """
    
    valid_sizes = [OpSize.BYTE, OpSize.WORD, OpSize.LONG]

    def __init__(self, params: list, size: OpSize=OpSize.WORD):
        assert len(params) == 2
        assert isinstance(params[0], AssemblyParameter)
        assert isinstance(params[1], AssemblyParameter)

        # check src param is valid
        assert params[0].mode == EAMode.IMM
        self.src = params[0]

        # check the dest param is valid
        assert params[1].mode != EAMode.ARD or params[1].mode != EAMode.IMM
        self.dest = params[1]

        assert size in Ori.valid_sizes
        self.size = size

    def assemble(self) -> bytearray:
        """
        Assembles this opcode into hex to be inserted into memory
        :return: The hex version of this opcode
        """

        # The first 8 bits are always 0
        ret_opcode = 0

        if self.size == OpSize.BYTE:
            ret_opcode |= 0b00 << 6
        elif self.size == OpSize.WORD:
            ret_opcode |= 0b01 << 6
        elif self.size == OpSize.LONG:
            ret_opcode |= 0b10 << 6

        ret_opcode |= ea_mode_bin.parse_from_ea_mode_modefirst(self.dest) << 0

        ret_bytes = bytearray(ret_opcode.to_bytes(OpSize.WORD.value, byteorder='big', signed=False))

        ret_bytes.extend(opcode_util.ea_to_binary_post_op(self.src, self.size).get_value_bytearray())

        if self.dest.mode == EAMode.AWA or self.dest.mode == EAMode.ALA:
            ret_bytes.extend(opcode_util.ea_to_binary_post_op(self.dest, self.size).get_value_bytearray())

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

        # add the length of the size of the operation, in words
        if self.size is OpSize.BYTE:
            to_increment += OpSize.WORD.value
        else:
            to_increment += self.size.value

        # repeat for the dest
        if self.dest.mode in [EAMode.AbsoluteLongAddress]:
            to_increment += OpSize.LONG.value

        if self.dest.mode in [EAMode.AbsoluteWordAddress]:
            to_increment += OpSize.WORD.value

        result_unsigned = src_val.get_value_unsigned() | dest_val.get_value_unsigned()

        msb_bit = 0

        if self.size is OpSize.BYTE:
            msb_bit = 0x80
        elif self.size is OpSize.WORD:
            msb_bit = 0x8000
        elif self.size is OpSize.LONG:
            msb_bit = 0x80000000
        
        # set hte FONCKin CCR
        simulator.set_ccr_reg(None, (msb_bit & result_unsigned != 0), (result_unsigned == 0), False, False)

        # and set the value
        self.dest.set_value(simulator, MemoryValue(OpSize.LONG, unsigned_int=result_unsigned))

        # set the program counter value
        simulator.increment_program_counter(to_increment)

    def __str__(self):
        return 'Ori command: size {}, src {}, dest {}'.format(self.size, self.src, self.dest)

    @classmethod
    def command_matches(cls, command: str) -> bool:
        """
        Checks whether a command string is an instance of this command type
        :param command: The command string to check (e.g. 'MOVE.B', 'LEA', etc.)
        :return: Whether the string is an instance of this command type
        """
        return opcode_util.command_matches(command, 'ORI')

    @classmethod
    def get_word_length(cls, command: str, parameters: str) -> int:
        """
        >>> Ori.get_word_length('ORI.B', '#$08, D1')
        2

        >>> Ori.get_word_length('ORI.B', '#$F1, D3')
        2

        >>> Ori.get_word_length('ORI.W', '#$ABCDE, D0')
        2

        >>> Ori.get_word_length('ORI.W', '#$000A, ($7000).W')
        3

        >>> Ori.get_word_length('ORI.L', '#$FFFF7000, ($1234).W')
        4

        >>> Ori.get_word_length('ORI.L', '#$FFFFFFFF, ($FFFF).L')
        5

        Gets what the end length of this command will be in memory
        :param command: The text of the command itself (e.g. "LEA", "MOVE.B", etc.)
        :param parameters: The parameters after the command
        :return: The length of the bytes in memory in words, as well as a list of warnings or errors encountered
        """
        parts = command.split('.')  # Split the command by period to get the size of the command
        if len(parts) == 1:  # Use the default size
            size = OpSize.WORD
        else:
            size = OpSize.parse(parts[1])

        # Split the parameters into EA modes
        params = parameters.split(',')

        dest = parse_assembly_parameter(params[1].strip())

        length = 1  # Always 1 word not counting additions to end

        if size == OpSize.LONG:
            length += 2  # Longs are 2 words long
        else:
            length += 1  # This is a word or byte, so only 1 word

        if dest.mode == EAMode.AWA:  # Appends a word
            length += 1

        if dest.mode == EAMode.ALA:  # Appends a long, so 2 words
            length += 2

        return length

    @classmethod
    def is_valid(cls, command: str, parameters: str) -> (bool, list):
        """
        Tests whether the given command is valid

        >>> Ori.is_valid('ORI.B', '#$1, D1')[0]
        True

        >>> Ori.is_valid('ORI.W', 'A3, D7')[0]
        False

        >>> Ori.is_valid('ORI.L', '#$ABCD, D3')[0]
        True

        >>> Ori.is_valid('ORI.L', '#$A0008000, D5')[0]
        True

        >>> Ori.is_valid('ORR.W', '#AB, D3')[0]
        False

        >>> Ori.is_valid('OR.G', 'D0, D7')[0]
        False

        :param command: The command itself (e.g. 'MOVE.B', 'LEA', etc.)
        :param parameters: The parameters after the command (such as the source and destination of a move)
        :return: Whether the given command is valid and a list of issues/warnings encountered
        """
        return opcode_util.n_param_is_valid(command, parameters, "ORI", 2, param_invalid_modes=[
            [EAMode.DRD, EAMode.ARD, EAMode.ARI, EAMode.ARIPI, EAMode.ARIPD, EAMode.AWA, EAMode.ALA]
            ,[EAMode.ARD, EAMode.IMM]])[:2]

    @classmethod
    def disassemble_instruction(cls, data: bytearray) -> Opcode:
        """
        This has a non-ORI opcode
        >>> Ori.disassemble_instruction(bytearray.fromhex('D280'))


        ORI.B #0, D1
        >>> op = Ori.disassemble_instruction(bytearray.fromhex('00010000'))

        >>> str(op.src)
        'EA Mode: EAMode.IMM, Data: 0'

        >>> str(op.dest)
        'EA Mode: EAMode.DRD, Data: 1'

        ORI.W #$A000, D0
        >>> op = Ori.disassemble_instruction(bytearray.fromhex('0040A000'))

        >>> str(op.src)
        'EA Mode: EAMode.IMM, Data: 40960'

        >>> str(op.dest)
        'EA Mode: EAMode.DRD, Data: 0'

        ORI.L #$FFFF0000, D7
        >>> op = Ori.disassemble_instruction(bytearray.fromhex('0087FFFF0000'))

        >>> str(op.src)
        'EA Mode: EAMode.IMM, Data: 4294901760'

        >>> str(op.dest)
        'EA Mode: EAMode.DRD, Data: 7'

        ORI.W #$FFFF, ($1234).W
        >>> op = Ori.disassemble_instruction(bytearray.fromhex('0078FFFF1234'))

        >>> str(op.src)
        'EA Mode: EAMode.IMM, Data: 65535'

        >>> str(op.dest)
        'EA Mode: EAMode.AWA, Data: 4660'

        Parses some raw data into an instance of the opcode class
        :param data: The data used to convert into an opcode instance
        :return: The constructed instance or none if there was an error and
            the amount of data in words that was used (e.g. extra for immediate
            data) or 0 for not a match
        """
        assert len(data) >= 2, 'Opcode size is at least one word'

        first_word = int.from_bytes(data[0:2], 'big')
        [opcode_bin,
         size_bin,
         ea_mode_bin,
         ea_reg_bin] = split_bits(first_word, [8, 2, 3, 3])

        if opcode_bin != 0b00000000:
            return None

        # determine the size
        if size_bin == 0b00:
            size = OpSize.BYTE
        elif size_bin == 0b01:
            size = OpSize.WORD
        elif size_bin == 0b10:
            size = OpSize.LONG
        else:
            return None

        # set the source
        src = parse_ea_from_binary(0b111, 0b100, size, True, data[2:])[0]

        # set the destination
        dest = parse_ea_from_binary(ea_mode_bin, ea_reg_bin, size, False, data[4:])[0]

        return cls([src, dest], size)

    @classmethod
    def from_str(cls, command: str, parameters: str):
        """
        Parses a ORI command from text.
        >>> str(Ori.from_str('ORI.B', '#$2, D1'))
        'Ori command: size OpSize.BYTE, src EA Mode: EAMode.IMM, Data: 2, dest EA Mode: EAMode.DRD, Data: 1'
        >>> str(Ori.from_str('ORI.L', '#$FFFF8000, (A0)'))
        'Ori command: size OpSize.LONG, src EA Mode: EAMode.IMM, Data: 4294934528, dest EA Mode: EAMode.ARI, Data: 0'

        :param command: The command itself (e.g. 'MOVE.B', 'LEA', etc.)
        :param parameters: The parameters after the command (such as the source and destination of a move)
        :return: The parsed command
        """
        return opcode_util.n_param_from_str(command, parameters, Ori, 2, OpSize.WORD)
