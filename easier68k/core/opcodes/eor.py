from ...core.enum.ea_mode import EAMode
from ...core.models.assembly_parameter import AssemblyParameter
from ...core.enum import ea_mode_bin
from ...core.enum.ea_mode_bin import parse_ea_from_binary
from ...simulator.m68k import M68K
from ...core.util.split_bits import split_bits
from ...core.opcodes.opcode import Opcode
from ...core.util import opcode_util
from ...core.enum.op_size import OpSize
from ..util.parsing import parse_assembly_parameter
from ..enum.condition_status_code import ConditionStatusCode
from ..models.memory_value import MemoryValue


class Eor(Opcode):  # Forward declaration
    pass


class Eor(Opcode):
    """
    EOR: Exclusive-OR Logical

    Operation: Source ⊕ Destination → Destination

    Syntax: EOR Dn, < ea >

    Attributes: Size = (Byte, Word, Long)

    Description: Performs an exclusive-OR operation on the destination operand using the
    source operand and stores the result in the destination location. The size of the
    operation may be specified to be byte, word, or long. The source operand must be a
    data register. The destination operand is specified in the effective address field.

    Condition Codes:
    X — Not affected.
    N — Set if the most significant bit of the result is set; cleared otherwise.
    Z — Set if the result is zero; cleared otherwise.
    V — Always cleared.
    C — Always cleared.

    NOTE: Memory-to-data-register operations are not allowed. Most
    assemblers use EORI when the source is immediate data.
    """

    valid_sizes = [OpSize.BYTE, OpSize.WORD, OpSize.LONG]

    def __init__(self, params: list, size: OpSize=OpSize.WORD):
        assert len(params) == 2
        assert isinstance(params[0], AssemblyParameter)
        assert isinstance(params[1], AssemblyParameter)

        # check src param is valid
        assert params[0].mode == EAMode.DRD
        self.src = params[0]

        # check the dest param is valid
        assert params[1].mode != EAMode.ARD or params[1].mode != EAMode.IMM
        self.dest = params[1]

        assert size in Eor.valid_sizes
        self.size = size

    def assemble(self) -> bytearray:
        """
        Assembles this opcode into hex to be inserted into memory
        :return: The hex version of this opcode
        """
        # create the opcode
        ret_opcode = 0b1011 << 12
        ret_opcode |= self.src.data << 9

        if self.size == OpSize.BYTE:
            ret_opcode |= 0b100 << 6
        elif self.size == OpSize.WORD:
            ret_opcode |= 0b101 << 6
        elif self.size == OpSize.LONG:
            ret_opcode |= 0b110 << 6

        ret_opcode |= ea_mode_bin.parse_from_ea_mode_modefirst(self.dest) << 0

        ret_bytes = bytearray(ret_opcode.to_bytes(OpSize.WORD.value, byteorder='big', signed=False))

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

        elif self.dest.mode in [EAMode.AbsoluteWordAddress]:
            to_increment += OpSize.WORD.value

        result_unsigned = src_val.get_value_unsigned() ^ dest_val.get_value_unsigned()

        msb_bit = 0

        if self.size is OpSize.BYTE:
            msb_bit = 0x80
        elif self.size is OpSize.WORD:
            msb_bit = 0x8000
        elif self.size is OpSize.LONG:
            msb_bit = 0x80000000
        
        # set CCR
        simulator.set_ccr_reg(None, (msb_bit & result_unsigned != 0), (result_unsigned == 0), False, False)

        # and set the value
        self.dest.set_value(simulator, MemoryValue(OpSize.LONG, unsigned_int=result_unsigned))

        # set the program counter value
        simulator.increment_program_counter(to_increment)

    def __str__(self):
        return 'Eor command: size {}, src {}, dest {}'.format(self.size, self.src, self.dest)

    @classmethod
    def command_matches(cls, command: str) -> bool:
        """
        Checks whether a command string is an instance of this command type
        :param command: The command string to check (e.g. 'MOVE.B', 'LEA', etc.)
        :return: Whether the string is an instance of this command type
        """
        return opcode_util.command_matches(command, 'EOR')

    @classmethod
    def get_word_length(cls, command: str, parameters: str) -> int:
        """
        >>> Eor.get_word_length('EOR.B', 'D0, D1')
        1

        >>> Eor.get_word_length('EOR.W', 'D3, (A4)+')
        1

        >>> Eor.get_word_length('EOR.L', 'D1, ($1234).W')
        2

        >>> Eor.get_word_length('EOR.L', 'D0, ($FFFF).L')
        3

        >>> Eor.get_word_length('EOR.B', 'D0, -(A3)')
        1

        >>> Eor.get_word_length('EOR.W', 'D7, (A0)')
        1

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

        elif dest.mode == EAMode.ALA:  # Appends a long, so 2 words
            length += 2

        return length

    @classmethod
    def is_valid(cls, command: str, parameters: str) -> (bool, list):
        """
        Tests whether the given command is valid

        >>> Eor.is_valid('EOR.B', 'D0, D1')[0]
        True

        >>> Eor.is_valid('EOR.W', 'A3, D7')[0]
        False

        >>> Eor.is_valid('EOR.L', 'D5, ($1234).W')[0]
        True

        >>> Eor.is_valid('EOR.W', 'D5, ($0A0B).L')[0]
        True

        >>> Eor.is_valid('EOR.W', '#$AB, D3')[0]
        False

        >>> Eor.is_valid('EOR.G', 'D0, D7')[0]
        False

        :param command: The command itself (e.g. 'MOVE.B', 'LEA', etc.)
        :param parameters: The parameters after the command (such as the source and destination of a move)
        :return: Whether the given command is valid and a list of issues/warnings encountered
        """
        return opcode_util.n_param_is_valid(command, parameters, "EOR", 2, param_invalid_modes=[
            [EAMode.IMM, EAMode.ARD, EAMode.ARI, EAMode.ARIPI, EAMode.ARIPD, EAMode.AWA, EAMode.ALA]
            ,[EAMode.ARD, EAMode.IMM]])[:2]

    @classmethod
    def disassemble_instruction(cls, data: bytearray) -> Opcode:
        """
        This has a non-EOR opcode
        >>> Eor.disassemble_instruction(bytearray.fromhex('D280'))


        EOR.B D0, D1
        >>> op = Eor.disassemble_instruction(bytearray.fromhex('B101'))

        >>> str(op.src)
        'EA Mode: EAMode.DRD, Data: 0'

        >>> str(op.dest)
        'EA Mode: EAMode.DRD, Data: 1'

        EOR.W D3, D0
        >>> op = Eor.disassemble_instruction(bytearray.fromhex('B740'))

        >>> str(op.src)
        'EA Mode: EAMode.DRD, Data: 3'

        >>> str(op.dest)
        'EA Mode: EAMode.DRD, Data: 0'

        EOR.L D7, $1234
        >>> op = Eor.disassemble_instruction(bytearray.fromhex('BFB81234'))

        >>> str(op.src)
        'EA Mode: EAMode.DRD, Data: 7'

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
         register_bin,
         opmode_bin,
         ea_mode_binary,
         ea_reg_bin] = split_bits(first_word, [4, 3, 3, 3, 3])

        if opcode_bin != 0b1011:
            return None

        # determine the size
        if opmode_bin == 0b100:
            size = OpSize.BYTE
        elif opmode_bin == 0b101:
            size = OpSize.WORD
        elif opmode_bin == 0b110:
            size = OpSize.LONG
        else:
            return None

        # set the source
        src = parse_ea_from_binary(0b000, register_bin, size, True, data[2:])[0]

        # set the destination
        dest = parse_ea_from_binary(ea_mode_binary, ea_reg_bin, size, False, data[2:])[0]

        return cls([src, dest], size)

    @classmethod
    def from_str(cls, command: str, parameters: str):
        """
        Parses a MOVE command from text.
        >>> str(Eor.from_str('EOR.B', 'D1, -(A0)'))
        'Eor command: size OpSize.BYTE, src EA Mode: EAMode.DRD, Data: 1, dest EA Mode: EAMode.ARIPD, Data: 0'
        >>> str(Eor.from_str('EOR.L', 'D3, (A2)'))
        'Eor command: size OpSize.LONG, src EA Mode: EAMode.DRD, Data: 3, dest EA Mode: EAMode.ARI, Data: 2'

        :param command: The command itself (e.g. 'MOVE.B', 'LEA', etc.)
        :param parameters: The parameters after the command (such as the source and destination of a move)
        :return: The parsed command
        """
        return opcode_util.n_param_from_str(command, parameters, Eor, 2, OpSize.WORD)
