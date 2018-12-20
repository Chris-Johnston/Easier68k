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


class Neg(Opcode):
    """
    NEG: Negate
    Operation: 0 - Destination -> Destination
    Assembler Syntax: NEG <ea>
    Attributes: Size = (Byte, Word, Long)
    Description: Subtracts the destination operand from zero
                 and stores the result in the destination location.
                 The size of the operation is specified as byte, word, or long.
    Condition Codes: X - Set the same as the carry bit.
                     N - Set if the result is negative; cleared otherwise.
                     Z - Set if the result is zero; cleared otherwise.
                     V - Set if an overflow occurs; cleared otherwise.
                     C - Cleared if the result is zero; set otherwise.
    Instruction Format: 01000100 Signature xx Size xxx EAMode xxx EARegister
    Instruction Fields:
        Size field - Specifies the size of the operation.
            00 - Byte operation.
            01 - Word operation.
            10 - Long operation.
        Effective Address field - Specifies the address of the next instruction.
                                  Only data alterable addressing modes can be used.
            Valid Modes - Dn, (An), (An)+, -(An), (xxx).W, (xxx).L
    """

    # Allowed sizes for this opcode
    valid_sizes = [OpSize.BYTE, OpSize.WORD, OpSize.LONG]

    def __init__(self, params: list, size: OpSize = OpSize.WORD):
        assert len(params) == 1
        assert isinstance(params[0], AssemblyParameter)

        # check ea param is valid
        assert params[0].mode != EAMode.ARD or params[0].mode != EAMode.IMM
        self.dest = params[0]

        assert size in Neg.valid_sizes
        self.size = size

    def assemble(self) -> bytearray:
        """
        Assembles this opcode into hex to be inserted into memory
        :return: The hex version of this opcode
        """

        # 01000100 Signature xx Size xxx EAMode xxx EARegister
        # ret_opcode is the binary value which represents the assembled instruction
        ret_opcode = 0b01000100 << 8

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
        raw_total = 0 - dest_val.get_value_unsigned()

        total = (raw_total & mask) | preserve

        negative_bit = 0

        if self.size is OpSize.BYTE:
            negative_bit = 0x80
        elif self.size is OpSize.WORD:
            negative_bit = 0x8000
        elif self.size is OpSize.LONG:
            negative_bit = 0x80000000

        negative = total & negative_bit > 0

        # Overflow occurs when a sign change occurs where it shouldn't occur.
        # For example:   0 - positive != positive.
        # other example: 0 - negative != negative
        # This doesn't make sense, so an overflow occurs
        overflow = False

        if total != 0:
            if dest_val.get_value_unsigned() & negative_bit == 0:  # If it is positive
                if total & negative_bit == 0:  # And total is positive
                    overflow = True
            elif dest_val.get_value_unsigned() & negative_bit > 0:  # If it is negative
                if total & negative_bit > 0:  # If the total is negative
                    overflow = True

        # Cleared if the result is 0.
        carry_bit = total != 0

        # set me some heckin status
        simulator.set_ccr_reg(carry_bit, negative, (total == 0), overflow, carry_bit)

        # and set the value
        self.dest.set_value(simulator, MemoryValue(OpSize.LONG, unsigned_int=total))

        # set the program counter value
        simulator.increment_program_counter(to_increment)

    def __str__(self):
        # Makes this a bit easier to read in doctest output
        return 'Neg command: Size {}, dest {}'.format(self.size, self.dest)

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
        >>> Neg.get_word_length('NEG.B', 'D3')
        1

        >>> Neg.get_word_length('NEG.W', '-(A5)')
        1

        >>> Neg.get_word_length('NEG.B', '($BBBB).W')
        2

        >>> Neg.get_word_length('NEG.W', '(A0)+')
        1

        >>> Neg.get_word_length('NEG.W', '($BBBB).W')
        2

        >>> Neg.get_word_length('NEG.L', '($BBBB).L')
        3

        Gets what the end length of this command will be in memory
        :param command: The text of the command itself (e.g. "LEA", "MOVE.B", etc.)
        :param parameters: The parameters after the command
        :return: The length of the bytes in memory in words, as well as a list of warnings or errors encountered
        """

        # Split the parameters into EA modes
        params = parameters.split(',')

        # src = parse_assembly_parameter(params[0].strip())  # Parse the source and make sure it parsed right
        dest = parse_assembly_parameter(params[0].strip())

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

        >>> Neg.is_valid('NEG.B', 'D1')[0]
        True

        >>> Neg.is_valid('NEG.W', '(A5)')[0]
        True

        >>> Neg.is_valid('NEG.B', '#5, D1')[0]
        False

        >>> Neg.is_valid('NEG.L', 'D2')[0]
        True

        >>> Neg.is_valid('NE.L', 'D1')[0]
        False

        >>> Neg.is_valid('NEG.', 'D1')[0]
        False

        >>> Neg.is_valid('NEG.W', '($7000).W')[0]
        True

        :param command: The command itself (e.g. 'MOVE.B', 'LEA', etc.)
        :param parameters: The parameters after the command (such as the source and destination of a move)
        :return: Whether the given command is valid and a list of issues/warnings encountered
        """
        return opcode_util.n_param_is_valid(command, parameters, "NEG", 1, param_invalid_modes=[[EAMode.ARD,
                                                                                                 EAMode.IMM]])[:2]

    @classmethod
    def disassemble_instruction(cls, data: bytearray) -> Opcode:
        """
        This has a non-subq opcode
        >>> Neg.disassemble_instruction(bytearray.fromhex('0280'))


        NEG.B D7
        >>> op = Neg.disassemble_instruction(bytearray.fromhex('4407'))

        >>> str(op.dest)
        'EA Mode: EAMode.DRD, Data: 7'


        NEG.W (A5)
        >>> op = Neg.disassemble_instruction(bytearray.fromhex('4455'))

        >>> str(op.dest)
        'EA Mode: EAMode.ARI, Data: 5'

        NEG.L (A0)+
        >>> op = Neg.disassemble_instruction(bytearray.fromhex('4498'))

        >>> str(op.dest)
        'EA Mode: EAMode.ARIPI, Data: 0'

        NEG.W $4000
        >>> op = Neg.disassemble_instruction(bytearray.fromhex('44784000'))

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
         size_bin,
         ea_mode_binary,
         ea_reg_bin] = split_bits(first_word, [8, 2, 3, 3])

        if opcode_bin != 0b01000100:
            return None

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
        dest = parse_ea_from_binary(ea_mode_binary, ea_reg_bin, size, False, data[2:])[0]

        return cls([dest], size)

    @classmethod
    def from_str(cls, command: str, parameters: str):
        """
        Parses a NEG command from text.

        >>> str(Neg.from_str('NEG.B', 'D1'))
        'Neg command: Size OpSize.BYTE, dest EA Mode: EAMode.DRD, Data: 1'

        >>> str(Neg.from_str('NEG.L', '(A0)'))
        'Neg command: Size OpSize.LONG, dest EA Mode: EAMode.ARI, Data: 0'

        :param command: The command itself (e.g. 'MOVE.B', 'LEA', etc.)
        :param parameters: The parameters after the command (such as the source and destination of a move)
        :return: The parsed command
        """
        return opcode_util.n_param_from_str(command, parameters, Neg, 1, OpSize.WORD)
