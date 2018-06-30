from ...core.enum.ea_mode import EAMode
from ...core.enum.op_size import OpSize
from ...core.enum import ea_mode_bin
from ...core.enum.ea_mode_bin import parse_ea_from_binary
from ...simulator.m68k import M68K
from ...core.opcodes.opcode import Opcode
from ...core.util.split_bits import split_bits
from ...core.util import opcode_util
from ..util.parsing import parse_assembly_parameter
from ..models.assembly_parameter import AssemblyParameter
from ..enum.condition_status_code import ConditionStatusCode
from ..models.memory_value import MemoryValue


class Subq(Opcode):  # Forward declaration
    pass


class Subq(Opcode):
    # Allowed sizes for this opcode
    valid_sizes = [OpSize.BYTE, OpSize.WORD, OpSize.LONG]

    def __init__(self, params: list, size: OpSize = OpSize.WORD):
        assert len(params) == 2
        assert isinstance(params[0], AssemblyParameter)
        assert isinstance(params[1], AssemblyParameter)

        # check src param is valid
        assert params[0].mode == EAMode.IMM
        self.src = params[0]

        # check the dest param is valid. Can't be immediate data
        assert params[1].mode != EAMode.IMM
        self.dest = params[1]

        assert size in Subq.valid_sizes
        self.size = size

    def assemble(self) -> bytearray:
        """
        Assembles this opcode into hex to be inserted into memory
        :return: The hex version of this opcode
        """

        # 1101 Dn xxx D x S xx M xxx Xn xxx
        # ret_opcode is the binary value which represents the assembled instruction
        ret_opcode = 0b0101 << 12
        ret_opcode |= self.src.data << 9
        ret_opcode |= 0b1 << 8

        if self.size == OpSize.BYTE:
            ret_opcode |= 0b00 << 6
        elif self.size == OpSize.WORD:
            ret_opcode |= 0b01 << 6
        elif self.size == OpSize.LONG:
            ret_opcode |= 0b10 << 6

        ret_opcode |= ea_mode_bin.parse_from_ea_mode_modefirst(self.dest) << 0

        ret_bytes = bytearray(ret_opcode.to_bytes(2, byteorder='big', signed=False))

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

        # repeat for the dest
        if self.dest.mode in [EAMode.AbsoluteLongAddress]:
            to_increment += OpSize.LONG.value

        if self.dest.mode in [EAMode.AbsoluteWordAddress]:
            to_increment += OpSize.WORD.value

        # mask to apply to the source
        mask = 0xFF

        if self.size is OpSize.BYTE:
            mask = 0xFF
        if self.size is OpSize.WORD:
            mask = 0xFFFF
        if self.size is OpSize.LONG:
            mask = 0xFFFFFFFF

        # which bits of the total should not be modified
        inverted_mask = 0xFFFFFFFF ^ mask

        # preserve the upper bits of the operation if they aren't used
        preserve = dest_val.get_value_signed() & inverted_mask
        raw_total = dest_val.get_value_unsigned() - src_val.get_value_unsigned()

        total = (raw_total & mask) | preserve

        # If the subtraction of the masked destination and source value is
        # negative, then a borrow has been generated.
        borrow_bit = (mask & dest_val.get_value_unsigned()) - src_val.get_value_unsigned() < 0

        negative_bit = 0

        if self.size is OpSize.BYTE:
            negative_bit = 0x80
        elif self.size is OpSize.WORD:
            negative_bit = 0x8000
        elif self.size is OpSize.LONG:
            negative_bit = 0x80000000

        negative = total & negative_bit > 0

        # Overflow occurs when a sign change occurs where it shouldn't occur.
        # For example: positive - negative != negative.
        # This doesn't make sense, so an overflow occurs
        overflow = False

        if dest_val.get_value_unsigned() & 0x80000000 > 0:
            if total & negative_bit == 0:
                overflow = True

        # set the same as the 'C' bit
        simulator.set_condition_status_code(ConditionStatusCode.X, borrow_bit)
        # set if result is negative
        simulator.set_condition_status_code(ConditionStatusCode.N, negative)
        # set if result is zero
        simulator.set_condition_status_code(ConditionStatusCode.Z, total == 0)
        # set if an overflow is generated, cleared otherwise
        simulator.set_condition_status_code(ConditionStatusCode.V, overflow)
        # set if a borrow is generated, cleared otherwise
        simulator.set_condition_status_code(ConditionStatusCode.C, borrow_bit)

        # and set the value
        self.dest.set_value(simulator, MemoryValue(OpSize.LONG, unsigned_int=total))

        # set the program counter value
        simulator.increment_program_counter(to_increment)

    def __str__(self):
        # Makes this a bit easier to read in doctest output
        return 'Subq command: Size {}, src {}, dest {}'.format(self.size, self.src, self.dest)

    @classmethod
    def command_matches(cls, command: str) -> bool:
        """
        Checks whether a command string is an instance of this command type
        :param command: The command string to check (e.g. 'MOVE.B', 'LEA', etc.)
        :return: Whether the string is an instance of this command type
        """
        return opcode_util.command_matches(command, 'SUB')

    @classmethod
    def get_word_length(cls, command: str, parameters: str) -> int:
        """
        >>> Subq.get_word_length('SUBQ.B', '#5, D3')
        1

        >>> Subq.get_word_length('SUBQ.W', '#4, ($BBBB).W')
        2

        >>> Subq.get_word_length('SUBQ.L', '#7, ($BBBB).W')
        2

        >>> Subq.get_word_length('SUBQ.W', '#1, ($BBBB).L')
        3

        >>> Subq.get_word_length('SUBQ.W', '#8, ($BBBB).L')
        3

        >>> Subq.get_word_length('SUB.L', '#5, ($BBBB).L')
        3

        Gets what the end length of this command will be in memory
        :param command: The text of the command itself (e.g. "LEA", "MOVE.B", etc.)
        :param parameters: The parameters after the command
        :return: The length of the bytes in memory in words, as well as a list of warnings or errors encountered
        """

        # Split the parameters into EA modes
        params = parameters.split(',')

        # src = parse_assembly_parameter(params[0].strip())  # Parse the source and make sure it parsed right
        dest = parse_assembly_parameter(params[1].strip())

        length = 1  # Always 1 word not counting additions to end

        if dest.mode == EAMode.AWA:  # Appends a word
            length += 1

        if dest.mode == EAMode.ALA:  # Appends a long, so 2 words
            length += 2

        return length

    @classmethod
    def is_valid(cls, command: str, parameters: str) -> (bool, list):
        """
        Tests whether the given command is valid

        >>> Subq.is_valid('SUBQ.B', '#2, D1')[0]
        True

        >>> Subq.is_valid('SUBQ.W', 'D0')[0]
        False

        >>> Subq.is_valid('SUBQ.G', '#5, D1')[0]
        False

        >>> Subq.is_valid('SUBQ.L', 'D0, A2')[0]
        False

        >>> Subq.is_valid('SU.L', '#2, D1')[0]
        False

        >>> Subq.is_valid('SUBQ.', '#5, D1')[0]
        False

        >>> Subq.is_valid('SUBQ.W', '#2, #6500')[0]
        False

        :param command: The command itself (e.g. 'MOVE.B', 'LEA', etc.)
        :param parameters: The parameters after the command (such as the source and destination of a move)
        :return: Whether the given command is valid and a list of issues/warnings encountered
        """
        return opcode_util.n_param_is_valid(command, parameters, "SUBQ", 2, param_invalid_modes=[[EAMode.ARD],
                                                                                                [EAMode.ARD,
                                                                                                 EAMode.IMM]])[:2]

    @classmethod
    def disassemble_instruction(cls, data: bytearray) -> Opcode:
        """
        This has a non-subq opcode
        >>> Subq.disassemble_instruction(bytearray.fromhex('0280'))


        SUBQ.B #2,D7
        >>> op = Subq.disassemble_instruction(bytearray.fromhex('5507'))

        >>> str(op.src)
        'EA Mode: EAMode.IMM, Data: 2'

        >>> str(op.dest)
        'EA Mode: EAMode.DRD, Data: 7'


        SUBQ.W #5,D1
        >>> op = Subq.disassemble_instruction(bytearray.fromhex('5B41'))

        >>> str(op.src)
        'EA Mode: EAMode.IMM, Data: 5'

        >>> str(op.dest)
        'EA Mode: EAMode.DRD, Data: 1'

        SUBQ.L #7,(A0)
        >>> op = Subq.disassemble_instruction(bytearray.fromhex('5F90'))

        >>> str(op.src)
        'EA Mode: EAMode.IMM, Data: 7'

        >>> str(op.dest)
        'EA Mode: EAMode.ARI, Data: 0'

        SUBQ.L #3,$4000
        >>> op = Subq.disassemble_instruction(bytearray.fromhex('57B84000'))

        >>> str(op.src)
        'EA Mode: EAMode.IMM, Data: 3'

        >>> str(op.dest)
        'EA Mode: EAMode.AWA, Data: 16384'

        Parses some raw data into an instance of the opcode class
        :param data: The data used to convert into an opcode instance
        :return: The constructed instance or none if there was an error and
            the amount of data in words that was used (e.g. extra for immediate
            data) or 0 for not a match
        """
        assert len(data) >= 2, 'Opcode size is at least one word'

        first_word = int.from_bytes(data[0:2], 'big')
        [opcode_bin,
         data_bin,
         one_bin,
         size_bin,
         ea_mode_binary,
         ea_reg_bin] = split_bits(first_word, [4, 3, 1, 2, 3, 3])

        if opcode_bin != 0b0101 or one_bin != 0b1:
            return None

        src = None
        dest = None
        size = None

        # populate source data
        src = AssemblyParameter(EAMode.IMM, data_bin)

        # Determine size
        if size_bin == 0b00:
            size = OpSize.BYTE
        elif size_bin == 0b01:
            size = OpSize.WORD
        elif size_bin == 0b10:
            size = OpSize.LONG
        else:
            return None

        # populate destination data
        dest = dest = parse_ea_from_binary(ea_mode_binary, ea_reg_bin, size, False, data[2:])[0]

        return cls([src, dest], size)

    @classmethod
    def from_str(cls, command: str, parameters: str):
        """
        Parses a SUBQ command from text.

        >>> str(Subq.from_str('SUBQ.B', '#4, D1'))
        'Subq command: Size OpSize.BYTE, src EA Mode: EAMode.IMM, Data: 4, dest EA Mode: EAMode.DRD, Data: 1'

        >>> str(Subq.from_str('SUBQ.L', '#1, (A0)'))
        'Subq command: Size OpSize.LONG, src EA Mode: EAMode.IMM, Data: 1, dest EA Mode: EAMode.ARI, Data: 0'

        :param command: The command itself (e.g. 'MOVE.B', 'LEA', etc.)
        :param parameters: The parameters after the command (such as the source and destination of a move)
        :return: The parsed command
        """
        return opcode_util.n_param_from_str(command, parameters, Subq, 2, OpSize.WORD)
