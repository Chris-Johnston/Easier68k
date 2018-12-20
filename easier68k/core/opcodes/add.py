from ...core.enum.ea_mode import EAMode
from ...core.enum.op_size import MoveSize, OpSize
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


class Add(Opcode):  # Forward declaration
    pass


class Add(Opcode):
    # Allowed sizes for this opcode
    valid_sizes = [OpSize.BYTE, OpSize.WORD, OpSize.LONG]

    def __init__(self, params: list, size: OpSize = OpSize.WORD):
        assert len(params) == 2
        assert isinstance(params[0], AssemblyParameter)
        assert isinstance(params[1], AssemblyParameter)

        # check src param is valid
        assert params[0].mode != EAMode.ARD
        self.src = params[0]

        # check the dest param is valid

        # one of the modes must be DRD
        if (params[0].mode != EAMode.DRD):
            assert params[1].mode == EAMode.DRD
        assert params[1] != EAMode.ARD and params[1] != EAMode.IMM
        self.dest = params[1]

        assert size in Add.valid_sizes
        self.size = size

    def assemble(self) -> bytearray:
        """
        Assembles this opcode into hex to be inserted into memory
        :return: The hex version of this opcode
        """

        # 1101 Dn xxx D x S xx M xxx Xn xxx
        # ret_opcode is the binary value which represents the assembled instruction
        ret_opcode = 0b1101 << 12

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
        raw_total = src_val.get_value_unsigned() + dest_val.get_value_unsigned()

        total = (raw_total & mask) | preserve

        carry_bit = False

        # if the total is greater than the maximum size for the operation
        # then the carry bit will be set
        if self.size is OpSize.BYTE and raw_total > 0xFF:
            carry_bit = True
        if self.size is OpSize.WORD and raw_total > 0xFFFF:
            carry_bit = True
        if self.size is OpSize.LONG and raw_total > 0xFFFFFFFF:
            carry_bit = True

        negative = False

        if self.size is OpSize.BYTE:
            negative = total & 0x80 > 0
        elif self.size is OpSize.WORD:
            negative = total & 0x8000 > 0
        elif self.size is OpSize.LONG:
            negative = total & 0x80000000 > 0

        original_negative = src_val.get_negative()

        # set the CCR
        simulator.set_ccr_reg(carry_bit, negative, ((total & mask) == 0), (negative != original_negative), carry_bit)

        # and set the value
        self.dest.set_value(simulator, MemoryValue(OpSize.LONG, unsigned_int=(total & mask)))

        # set the program counter value
        simulator.increment_program_counter(to_increment)

    def __str__(self):
        # Makes this a bit easier to read in doctest output
        return 'Add command: Size {}, src {}, dest {}'.format(self.size, self.src, self.dest)

    @classmethod
    def command_matches(cls, command: str) -> bool:
        """
        Checks whether a command string is an instance of this command type
        :param command: The command string to check (e.g. 'MOVE.B', 'LEA', etc.)
        :return: Whether the string is an instance of this command type
        """
        return opcode_util.command_matches(command, 'ADD')

    @classmethod
    def get_word_length(cls, command: str, parameters: str) -> int:
        """
        >>> Add.get_word_length('ADD', 'D0, D1')
        1

        >>> Add.get_word_length('ADD.L', '#$90, D3')
        3

        >>> Add.get_word_length('ADD.W', '#$90, D3')
        2

        >>> Add.get_word_length('ADD.W', '($AAAA).L, D7')
        3

        >>> Add.get_word_length('ADD.W', 'D0, ($BBBB).L')
        3

        >>> Add.get_word_length('ADD.W', '($AAAA).L, ($BBBB).L')
        5

        >>> Add.get_word_length('ADD.W', '#$AAAA, ($BBBB).L')
        4

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

        >>> Add.is_valid('ADD.B', 'D0, D1')[0]
        True

        >>> Add.is_valid('ADD.W', 'D0')[0]
        False

        >>> Add.is_valid('ADD.G', 'D0, D1')[0]
        False

        >>> Add.is_valid('ADD.L', 'D0, A2')[0]
        False

        >>> Add.is_valid('AD.L', 'D0, D1')[0]
        False

        >>> Add.is_valid('ADD.', 'D0, D1')[0]
        False

        :param command: The command itself (e.g. 'MOVE.B', 'LEA', etc.)
        :param parameters: The parameters after the command (such as the source and destination of a move)
        :return: Whether the given command is valid and a list of issues/warnings encountered
        """
        return opcode_util.n_param_is_valid(command, parameters, "ADD", 2, param_invalid_modes=[[EAMode.ARD],
                                                                                                [EAMode.ARD,
                                                                                                 EAMode.IMM]])[:2]

    @classmethod
    def disassemble_instruction(cls, data: bytearray) -> Opcode:
        """
        This has a non-add opcode
        >>> Add.disassemble_instruction(bytearray.fromhex('0280'))


        ADD.B D1,D7
        >>> op = Add.disassemble_instruction(bytearray.fromhex('D307'))

        >>> str(op.src)
        'EA Mode: EAMode.DRD, Data: 1'

        >>> str(op.dest)
        'EA Mode: EAMode.DRD, Data: 7'


        ADD.B #0, D1
        >>> op = Add.disassemble_instruction(bytearray.fromhex('D23C00'))

        >>> str(op.src)
        'EA Mode: EAMode.IMM, Data: 0'

        >>> str(op.dest)
        'EA Mode: EAMode.DRD, Data: 1'

        ADD.W D3, D0
        >>> op = Add.disassemble_instruction(bytearray.fromhex('D740'))

        >>> str(op.src)
        'EA Mode: EAMode.DRD, Data: 3'

        >>> str(op.dest)
        'EA Mode: EAMode.DRD, Data: 0'

        ADD.L ($0A0B0C0D).L, D7
        >>> op = Add.disassemble_instruction(bytearray.fromhex('DEB9000A0B0C'))

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

        if opcode_bin != 0b1101:
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
        Parses a ADD command from text.

        >>> str(Add.from_str('ADD.B', '-(A0), D1'))
        'Add command: Size OpSize.BYTE, src EA Mode: EAMode.ARIPD, Data: 0, dest EA Mode: EAMode.DRD, Data: 1'

        >>> str(Add.from_str('ADD.L', 'D3, (A0)'))
        'Add command: Size OpSize.LONG, src EA Mode: EAMode.DRD, Data: 3, dest EA Mode: EAMode.ARI, Data: 0'

        :param command: The command itself (e.g. 'MOVE.B', 'LEA', etc.)
        :param parameters: The parameters after the command (such as the source and destination of a move)
        :return: The parsed command
        """
        return opcode_util.n_param_from_str(command, parameters, Add, 2, OpSize.WORD)
