from ..ea_mode import EAMode
from ..assembly_parameter import AssemblyParameter
from ..ea_mode_bin import parse_ea_from_binary
from ..m68k import M68K
from ..split_bits import split_bits
from .opcode import Opcode
from ..op_size import OpSize
from ..parsing import parse_assembly_parameter
from ..condition_status_code import ConditionStatusCode


class Or(Opcode):
    """
    OR: Inclusive-OR Logical

    Operation: Source V Destination → Destination

    Syntax: 
    Type 1: OR < ea > ,Dn
    Type 2: OR Dn, < ea >
    
    Attributes: Size = (Byte, Word, Long)
    
    Description: Performs an inclusive-OR operation on the source operand and the
    destination operand and stores the result in the destination location. The size of the
    operation is specified as byte, word, or long. The contents of an address register may
    not be used as an operand.

    Condition Codes:
    X — Not affected.
    N — Set if the most significant bit of the result is set; cleared otherwise.
    Z — Set if the result is zero; cleared otherwise.
    V — Always cleared.
    C — Always cleared.

    Opmode field:
     Byte
     Word
     Long
 
    Type 1:
     000
     001
     010
 
    Type 2:
     100
     101
     110

    Operation:
    Type 1: < ea > V Dn → Dn
    Type 2: Dn V < ea > → < ea >

    NOTE: If the destination is a data register, it must be specified using the
    destination Dn mode, not the destination < ea > mode.
    Most assemblers use ORI when the source is immediate data.
    """

    valid_sizes = [OpSize.BYTE, OpSize.WORD, OpSize.LONG]

    def __init__(self, params: list, size: OpSize=OpSize.WORD):
        assert len(params) == 2
        assert isinstance(params[0], AssemblyParameter)
        assert isinstance(params[1], AssemblyParameter)

        # check src param is valid
        assert params[0].mode != EAMode.ARD
        self.src = params[0]

        # check the dest param is valid

        # one of the modes must be DRD
        if(params[0].mode != EAMode.DRD):
            assert params[1].mode == EAMode.DRD
        assert params[1].mode != EAMode.ARD and params[1].mode != EAMode.IMM
        self.dest = params[1]

        assert size in Or.valid_sizes
        self.size = size

    def assemble(self) -> bytearray:
        """
        Assembles this opcode into hex to be inserted into memory
        :return: The hex version of this opcode
        """
        # 1000 Dn xxx D x S xx M xxx Xn xxx
        # ret_opcode is the binary value which represents the assembled instruction
        ret_opcode = 0b1000 << 12

        if self.src == EAMode.DRD:
            ret_opcode |= self.src.data << 9

            if self.size == OpSize.BYTE:
                ret_opcode |= 0b100 << 6
            elif self.size == OpSize.WORD:
                ret_opcode |= 0b101 << 6
            elif self.size == OpSize.LONG:
                ret_opcode |= 0b110 << 6

            ret_opcode |= ea_mode_bin.parse_from_ea_mode_modefirst(self.dest)
        else:  # dest must be DRD
            ret_opcode |= self.dest.data << 9

            if self.size == OpSize.BYTE:
                # don't have to do anything, |= wouldn't do anything
                pass
            elif self.size == OpSize.WORD:
                ret_opcode |= 0b001 << 6
            elif self.size == OpSize.LONG:
                ret_opcode |= 0b010 << 6

            ret_opcode |= ea_mode_bin.parse_from_ea_mode_modefirst(self.src)

        # convert the int to a bytes, then to a mutable bytearray
        return bytearray(ret_opcode.to_bytes(2, byteorder='big', signed=False))

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

        result = src_val | dest_val
        result_unsigned = result.get_value_unsigned()

        msb_bit = 0

        if self.size is OpSize.BYTE:
            msb_bit = 0x80
        elif self.size is OpSize.WORD:
            msb_bit = 0x8000
        elif self.size is OpSize.LONG:
            msb_bit = 0x80000000

        # set status codes
        simulator.set_ccr_reg(None, (msb_bit & result_unsigned != 0), (result_unsigned == 0), False, False)

        # and set the value
        self.dest.set_value(simulator, result)

        # set the program counter value
        simulator.increment_program_counter(to_increment)

    def __str__(self):
        return 'Or command: size {}, src {}, dest {}'.format(self.size, self.src, self.dest)

    @classmethod
    def command_matches(cls, command: str) -> bool:
        """
        Checks whether a command string is an instance of this command type
        :param command: The command string to check (e.g. 'MOVE.B', 'LEA', etc.)
        :return: Whether the string is an instance of this command type
        """
        return opcode_util.command_matches(command, 'OR')

    @classmethod
    def get_word_length(cls, command: str, parameters: str) -> int:
        """
        >>> Or.get_word_length('OR.W', '(A0), D1')
        1

        >>> Or.get_word_length('OR.W', '#$0, D3')
        2

        >>> Or.get_word_length('OR.L', '#$ABCDE, D0')
        3

        >>> Or.get_word_length('OR.L', '#$A, D3')
        3

        >>> Or.get_word_length('OR.L', '($AAAA).L, D6')
        3

        >>> Or.get_word_length('OR.W', '($AAAA).W, D5')
        2

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

        >>> Or.is_valid('OR.B', 'D0, D1')[0]
        True

        >>> Or.is_valid('OR.W', 'A3, D7')[0]
        False

        >>> Or.is_valid('OR.L', '#$ABCD, D3')[0]
        True

        >>> Or.is_valid('OR.W', '($0A0B).L, D5')[0]
        True

        >>> Or.is_valid('ORR.W', '#AB, D3')[0]
        False

        >>> Or.is_valid('OR.G', 'D0, D7')[0]
        False

        :param command: The command itself (e.g. 'MOVE.B', 'LEA', etc.)
        :param parameters: The parameters after the command (such as the source and destination of a move)
        :return: Whether the given command is valid and a list of issues/warnings encountered
        """
        return opcode_util.n_param_is_valid(command, parameters, "OR", 2, param_invalid_modes=[[EAMode.ARD],
            [EAMode.ARD, EAMode.IMM]])[:2]

    @classmethod
    def disassemble_instruction(cls, data: bytearray) -> Opcode:
        """
        This has a non-OR opcode
        >>> Or.disassemble_instruction(bytearray.fromhex('D280'))


        OR.B #0, D1
        >>> op = Or.disassemble_instruction(bytearray.fromhex('823C00'))

        >>> str(op.src)
        'EA Mode: EAMode.IMM, Data: 0'

        >>> str(op.dest)
        'EA Mode: EAMode.DRD, Data: 1'

        OR.W D3, D0
        >>> op = Or.disassemble_instruction(bytearray.fromhex('8740'))

        >>> str(op.src)
        'EA Mode: EAMode.DRD, Data: 3'

        >>> str(op.dest)
        'EA Mode: EAMode.DRD, Data: 0'

        OR.L ($0A0B0C0D).L, D7
        >>> op = Or.disassemble_instruction(bytearray.fromhex('8EB9000A0B0C'))

        >>> str(op.src)
        'EA Mode: EAMode.ALA, Data: 658188'

        >>> str(op.dest)
        'EA Mode: EAMode.DRD, Data: 7'

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
         ea_mode_bin,
         ea_reg_bin] = split_bits(first_word, [4, 3, 3, 3, 3])

        if opcode_bin != 0b1000:
            return None

        src = None
        dest = None
        size = None
        words_used = 1

        if opmode_bin == 0b100:
            size = OpSize.BYTE
            src = AssemblyParameter(EAMode.DRD, register_bin)
            dest = parse_ea_from_binary(ea_mode_bin, ea_reg_bin, size, False, data[words_used * 2:])[0]
        elif opmode_bin == 0b101:
            size = OpSize.WORD
            src = AssemblyParameter(EAMode.DRD, register_bin)
            dest = parse_ea_from_binary(ea_mode_bin, ea_reg_bin, size, False, data[words_used * 2:])[0]
        elif opmode_bin == 0b110:
            size = OpSize.LONG
            src = AssemblyParameter(EAMode.DRD, register_bin)
            dest = parse_ea_from_binary(ea_mode_bin, ea_reg_bin, size, False, data[words_used * 2:])[0]
        elif opmode_bin == 0b000:
            size = OpSize.BYTE
            dest = AssemblyParameter(EAMode.DRD, register_bin)
            src = parse_ea_from_binary(ea_mode_bin, ea_reg_bin, size, True, data[words_used * 2:])[0]
        elif opmode_bin == 0b001:
            size = OpSize.WORD
            dest = AssemblyParameter(EAMode.DRD, register_bin)
            src = parse_ea_from_binary(ea_mode_bin, ea_reg_bin, size, True, data[words_used * 2:])[0]
        elif opmode_bin == 0b010:
            size = OpSize.LONG
            dest = AssemblyParameter(EAMode.DRD, register_bin)
            src = parse_ea_from_binary(ea_mode_bin, ea_reg_bin, size, True, data[words_used * 2:])[0]
        else:
            return None

        return cls([src, dest], size)

    @classmethod
    def from_str(cls, command: str, parameters: str):
        """
        Parses a MOVE command from text.
        >>> str(Or.from_str('OR.B', '-(A0), D1'))
        'Or command: size OpSize.BYTE, src EA Mode: EAMode.ARIPD, Data: 0, dest EA Mode: EAMode.DRD, Data: 1'
        >>> str(Or.from_str('OR.L', 'D3, (A0)'))
        'Or command: size OpSize.LONG, src EA Mode: EAMode.DRD, Data: 3, dest EA Mode: EAMode.ARI, Data: 0'

        :param command: The command itself (e.g. 'MOVE.B', 'LEA', etc.)
        :param parameters: The parameters after the command (such as the source and destination of a move)
        :return: The parsed command
        """
        return opcode_util.n_param_from_str(command, parameters, Or, 2, OpSize.WORD)
