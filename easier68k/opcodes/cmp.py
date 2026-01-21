from .opcode import Opcode
from ..ea_mode import EAMode
from ..op_size import OpSize
from ..ea_mode_bin import parse_ea_from_binary
from ..m68k import M68K
from ..split_bits import split_bits
from ..parsing import parse_assembly_parameter
from ..assembly_parameter import AssemblyParameter
from ..condition_status_code import ConditionStatusCode
from ..memory_value import MemoryValue, mask_value_for_length
from ..opcode_util import check_valid_command, n_param_is_valid, n_param_from_str, command_matches


class Cmp(Opcode):
    """
    CMP: Compare
    Operation: Destination - Source -> cc
    Assembler Syntax: CMP <ea>, Dn
    Attributes: Size = (Byte, Word, Long)
    Description: Subtracts the source operand from the destination data register
                 and sets the condition codes according to the result;
                 the data register is not changed.
                 The size of the operation can be byte, word, or long.
    Condition Codes: X - Not affected
                     N - Set if the result is negative; cleared otherwise.
                     Z - Set if the result is zero; cleared otherwise.
                     V - Set if an overflow occurs; cleared otherwise.
                     C - Set if a borrow occurs; cleared otherwise.
    Instruction Format: 1 0 1 1 Dest Register xxx OpMode xxx EA mode xxx Register xxx
    Instruction Fields:
        Register field - Specifies the destination data register.

        Opmode field [Operation: Dn - <ea>]
            000 - Byte
            001 - Word
            010 - Long

        Effective Address field - Specifies the source operand.
                                  All addressing modes can be used.
            Valid Modes - All (Word and Long size only for An)

    NOTE: CMPA is used when the destination is an address register.
          CMPI is used when the source is immediate data.
          CMPM is used for memory-to-memory compares.
          Most assemblers automatically make the distinction.
    """

    # the allowed sizes for this opcode
    valid_sizes = [OpSize.BYTE, OpSize.WORD, OpSize.LONG]

    def __init__(self, params: list, size: OpSize = OpSize.WORD):
        # ensure that the parameters are valid
        assert len(params) == 2
        assert isinstance(params[0], AssemblyParameter)
        assert isinstance(params[1], AssemblyParameter)

        # source (params[0]) can be any EA mode
        # ensure that the destination is Dn
        assert params[1].mode == EAMode.DataRegisterDirect

        self.src = params[0]
        self.dest = params[1]

        assert size in Cmp.valid_sizes
        self.size = size

    def assemble(self) -> bytearray:
        """
        Assembles this opcode into a bytearray to be inserted into memory
        :return: The bytearray which represents this assembled opcode
        """

        # 1 0 1 1 Dest Register xxx OpMode xxx EA mode xxx Register xxx
        ret_opcode = 0b1011 << 12
        # add the dest register in it's place
        ret_opcode |= self.dest.data << 9
        # add the OpMode bytes
        if self.size == OpSize.BYTE:
            ret_opcode |= 0b000 << 6
        elif self.size == OpSize.WORD:
            ret_opcode |= 0b001 << 6
        elif self.size == OpSize.LONG:
            ret_opcode |= 0b010 << 6

        # add the ea bits for the src
        # with mode first
        ret_opcode |= ea_mode_bin.parse_from_ea_mode_modefirst(self.src)

        # convert the int to bytes, then to a mutable bytearray
        return bytearray(ret_opcode.to_bytes(2, byteorder='big', signed=False))

    def execute(self, simulator: M68K):
        """
        Executes this command in the simulator

        Subtracts the source operand from the destination operand and
        set the condition codes accordingly. The destination must be a
        data register. The destination is not modified by this instruction.

        :param simulator: the simulator that this opcode is being run on
        :return:
        """

        # get the src and dest values
        src_val = self.src.get_value(simulator, self.size.get_number_of_bytes())
        dest_val = self.dest.get_value(simulator, self.size.get_number_of_bytes())

        comparison = dest_val.get_value_signed() - src_val.get_value_signed()
        raw_total = dest_val.get_value_unsigned() - src_val.get_value_unsigned()
        comp_mv = dest_val - src_val

        # mask out only the bits we need/want
        comp_mv = MemoryValue(self.size,
                              unsigned_int=mask_value_for_length(self.size, comp_mv.get_value_unsigned()))

        negative = False

        if self.size is OpSize.BYTE:
            negative = comparison & 0x80 > 0
        elif self.size is OpSize.WORD:
            negative = comparison & 0x8000 > 0
        elif self.size is OpSize.LONG:
            negative = comparison & 0x80000000 > 0

        max_val = 0  # Maximum value allowed for the given memory size

        if self.size is OpSize.BYTE:
            max_val = 0xFF
        elif self.size is OpSize.WORD:
            max_val = 0xFFFF
        elif self.size is OpSize.LONG:
            max_val = 0xFFFFFFFF

        # Overflow occurs if the result cannot be represented by the memory size
        # Get the signed value
        test_val = comp_mv.get_value_signed()

        # If it is negative, get the twos complement
        if test_val < 0:
            test_val = (abs(test_val) ^ 0xFFFFFFFF) + 1

        # Check to see if it can hold the value
        overflow = test_val > max_val

        # ignore the carry bit

        # set freakin ccr
        simulator.set_ccr_reg(None, negative, (comparison == 0), overflow, (raw_total < 0))

        # set the number of bytes to increment equal to the length of the
        # instruction (1 word)
        to_increment = OpSize.WORD.value

        if self.src.mode is EAMode.AbsoluteLongAddress:
            to_increment += OpSize.LONG.value
        if self.src.mode is EAMode.AbsoluteWordAddress:
            to_increment += OpSize.WORD.value

        # increment PC
        simulator.increment_program_counter(to_increment)

    def __str__(self):
        return 'CMP Size {}, Src {}, Dest {}'.format(self.size, self.src, self.dest)

    @classmethod
    def command_matches(cls, command: str) -> bool:
        """
        Checks whether a command string is an instance of this command type

        This will only allow for CMP. Not CMPA, CMPI, CMPM. While CMP is not
        checking for the types that would make it actually one of these
        different types, those instructions must be implemented separately.

        :param command: The command string to check 'CMP.W', 'CMP'
        :return: Whether the string is an instance of CMP
        """
        return command_matches(command, 'CMP')

    @classmethod
    def get_word_length(cls, command: str, parameters: str) -> int:
        """
        Gets the length of this command in memory, including the length of
        the single opcode and the length of any immediate parameter values

        >>> Cmp.get_word_length('CMP', 'D0, D1')
        1

        >>> Cmp.get_word_length('CMP.W', 'D0, D1')
        1

        >>> Cmp.get_word_length('CMP.L', 'D0, D1')
        1

        >>> Cmp.get_word_length('CMP.L', '($AAAA).L, D7')
        3

        :param command:
        :param parameters:
        :return:
        """
        # split the command to get the size, if specified
        parts = command.split('.')
        if len(parts) == 1:
            size = OpSize.WORD
        else:
            size = OpSize.parse(parts[1])

        params = parameters.split(',')

        # parse the src and dest parameters

        src = parse_assembly_parameter(params[0].strip())
        dest = parse_assembly_parameter(params[1].strip())

        # minimum length is always 1
        length = 1

        if src.mode == EAMode.IMM:
            # immediate data is 2 words long
            if size == OpSize.LONG:
                length += 2
            else:
                # bytes and words are 1 word long
                length += 1

        if src.mode == EAMode.AWA:
            # appends a word
            length += 1

        if src.mode == EAMode.ALA:
            # appends a long
            length += 2

        return length

    @classmethod
    def is_valid(cls, command: str, parameters: str) -> (bool, list):
        """
        Tests whether the given command is valid

        >>> Cmp.is_valid('CMP', 'D0, D1')[0]
        True

        >>> Cmp.is_valid('CMP.', '#123, D7')[0]
        False

        :param command:
        :param parameters:
        :return:
        """
        # don't bother with param invalid modes
        return n_param_is_valid(
            command,
            parameters,
            "CMP",
            2)

    @classmethod
    def disassemble_instruction(cls, data: bytes) -> Opcode:
        """
        Disassembles the instruction into an instance of the CMP class
        :param data:
        :return:
        """
        assert len(data) >= 2, 'Opcode size must be at least 1 word'

        first_word = int.from_bytes(data[0:2], 'big')
        [opcode_bin,
         register_bin,
         opmode_bin,
         ea_mode_bin,
         ea_reg_bin] = split_bits(first_word, [4, 3, 3, 3, 3])

        # ensure that this is the correct opcode
        if opcode_bin != 0b1011:
            return None

        src = None
        dest = None
        size = None
        words_used = 1

        if opmode_bin == 0b000:
            size = OpSize.BYTE
        elif opcode_bin == 0b001:
            size = OpSize.WORD
        elif opcode_bin == 0b010:
            size = OpSize.LONG
        else:
            return None

        src = parse_ea_from_binary(ea_mode_bin, ea_reg_bin, size, True, data[words_used * 2:])[0]
        dest = AssemblyParameter(EAMode.DRD, register_bin)

        # make a new reference of this type
        return cls([src, dest], size)
    
    @classmethod
    def from_str(self, command: str, parameters: str):
        """
        Parses a CMP from text.

        :param command: The command itself 'CMP.L' 'CMP', etc.
        :param parameters: The parameters after the command
        :return: The parsed command
        """
        return n_param_from_str(command, parameters, Cmp, 2, OpSize.WORD)