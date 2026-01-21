from ..ea_mode import EAMode
from ..op_size import OpSize
from ..m68k import M68K
from .opcode import Opcode
from ..split_bits import split_bits
from ..parsing import parse_assembly_parameter
from ..assembly_parameter import AssemblyParameter
from ..memory_value import MemoryValue
from ..register import Register
from typing import Union
from ..ea_mode_bin import parse_from_ea_mode_modefirst
from ..opcode_util import check_valid_command, n_param_is_valid, n_param_from_str, command_matches, ea_to_binary_post_op


class Jsr(Opcode):
    """
    JSR: Jump to Subroutine
    Operation: SP - 4 -> SP; PC -> (SP); Destination Address -> PC
    Assembler Syntax: JSR <ea>
    Attributes: Unsized
    Description: Pushes the long-word address of the instruction immediately following the JSR instruction
                 onto the system stack. Program execution then continues
                 at the address specified in the instruction.
    Condition Codes: Not affected
    Instruction Format: 0100111010 Signature xxx EAMode xxx EARegister
    Instruction Field:
        Effective Address field - Speciﬁes the address of the next instruction.
                                  Only control addressing modes can be used as listed in the following tables.
        Valid Modes - (An), (xxx).W, (xxx).L
    """
    def __init__(self, params: list):
        assert len(params) == 1
        assert isinstance(params[0], AssemblyParameter)

        # check ea param is valid
        assert params[0].mode == EAMode.ARI or params[0].mode == EAMode.AWA or params[0].mode == EAMode.ALA
        self.dest = params[0]

    def assemble(self) -> bytearray:
        """
        Assembles this opcode into hex to be inserted into memory
        :return: The hex version of this opcode
        """

        # 0100111010 Signature xxx EAMode xxx EARegister
        # ret_opcode is the binary value which represents the assembled instruction
        ret_opcode = 0b0100111010 << 6

        ret_opcode |= parse_from_ea_mode_modefirst(self.dest) << 0

        ret_bytes = bytearray(ret_opcode.to_bytes(2, byteorder='big', signed=False))

        if self.dest.mode == EAMode.AWA or self.dest.mode == EAMode.ALA:
            size = OpSize.WORD if self.dest.mode == EAMode.AWA else OpSize.LONG
            ret_bytes.extend(ea_to_binary_post_op(self.dest, size).get_value_bytearray())

        return ret_bytes

    def execute(self, simulator: M68K):
        """
        Executes this command in a simulator
        :param simulator: The simulator to execute the command on
        :return: None
        """

        # increment the program counter by the length of the instruction (1 word)
        to_increment = OpSize.WORD.value

        # repeat for the dest
        if self.dest.mode in [EAMode.AbsoluteLongAddress]:
            to_increment += OpSize.LONG.value

        elif self.dest.mode in [EAMode.AbsoluteWordAddress]:
            to_increment += OpSize.WORD.value

        # set the program counter value
        simulator.increment_program_counter(to_increment)

        # get the value of src from the simulator
        dest_val = self.dest.get_value(simulator, OpSize.LONG)
        sp_val = simulator.get_register(Register.A7)
        new_sp_val = sp_val.get_value_unsigned() - 4

        # SP – 4 -> SP
        simulator.set_register(Register.A7, MemoryValue(OpSize.LONG, unsigned_int=new_sp_val))

        pc_val = simulator.get_program_counter_value()

        # PC -> (SP)
        AssemblyParameter(EAMode.ALA, new_sp_val).set_value(simulator, MemoryValue(OpSize.LONG, unsigned_int=pc_val))

        # Destination Address -> PC
        simulator.set_register(Register.PC, dest_val)

    def __str__(self):
        # Makes this a bit easier to read in doctest output
        return 'Jsr command: dest {}'.format(self.dest)

    @classmethod
    def command_matches(cls, command: str) -> bool:
        """
        Checks whether a command string is an instance of this command type
        :param command: The command string to check (e.g. 'MOVE.B', 'LEA', etc.)
        :return: Whether the string is an instance of this command type
        """
        return command_matches(command, 'JSR')

    @classmethod
    def get_word_length(cls, command: str, parameters: str) -> int:
        """
        >>> Jsr.get_word_length('JSR', '(A5)')
        1

        >>> Jsr.get_word_length('JSR', '-(A7)')
        1

        >>> Jsr.get_word_length('JSR', '($BBBB).W')
        2

        >>> Jsr.get_word_length('JSR', '($1000).W')
        2

        >>> Jsr.get_word_length('JSR', '($FFFF).L')
        3

        >>> Jsr.get_word_length('JSR', '($8000).L')
        3

        Gets what the end length of this command will be in memory
        :param command: The text of the command itself (e.g. "LEA", "MOVE.B", etc.)
        :param parameters: The parameters after the command
        :return: The length of the bytes in memory in words, as well as a list of warnings or errors encountered
        """

        dest = parse_assembly_parameter(parameters.strip())  # Parse the destination

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

        >>> Jsr.is_valid('JSR', '(A0)')[0]
        True

        >>> Jsr.is_valid('JSR', '(A5)')[0]
        True

        >>> Jsr.is_valid('JSR', '#5, D1')[0]
        False

        >>> Jsr.is_valid('JSR.W', '(A1)')[0]
        True

        >>> Jsr.is_valid('JS', '($1000).W')[0]
        False

        >>> Jsr.is_valid('JSR.', '(A4)')[0]
        False

        >>> Jsr.is_valid('JSR', '($7000).W')[0]
        True

        :param command: The command itself (e.g. 'MOVE.B', 'LEA', etc.)
        :param parameters: The parameters after the command (such as the source and destination of a move)
        :return: Whether the given command is valid and a list of issues/warnings encountered
        """
        return n_param_is_valid(command, parameters, "JSR", 1, param_invalid_modes=[[EAMode.DRD,
                                                                                                 EAMode.ARD,
                                                                                                 EAMode.ARIPD,
                                                                                                 EAMode.ARIPI,
                                                                                                 EAMode.IMM]])[:2]

    @classmethod
    def disassemble_instruction(cls, data: bytearray) -> Union[Opcode, None]:
        """
        This has a non-JSR opcode
        >>> Jsr.disassemble_instruction(bytearray.fromhex('0280'))


        JSR (A0)
        >>> op = Jsr.disassemble_instruction(bytearray.fromhex('4E90'))

        >>> str(op.dest)
        'EA Mode: EAMode.ARI, Data: 0'


        JSR (A5)
        >>> op = Jsr.disassemble_instruction(bytearray.fromhex('4E95'))

        >>> str(op.dest)
        'EA Mode: EAMode.ARI, Data: 5'

        JSR $4000
        >>> op = Jsr.disassemble_instruction(bytearray.fromhex('4EB84000'))

        >>> str(op.dest)
        'EA Mode: EAMode.AWA, Data: 16384'

        JSR $FFFF7000
        >>> op = Jsr.disassemble_instruction(bytearray.fromhex('4EB87000'))

        >>> str(op.dest)
        'EA Mode: EAMode.AWA, Data: 28672'

        Parses some raw data into an instance of the opcode class
        :param data: The data used to convert into an opcode instance
        :return: The constructed instance or none if there was an error and
            the amount of data in words that was used (e.g. extra for immediate
            data) or 0 for not a match
        """
        assert len(data) >= 2, 'Opcode size is at least one word'

        first_word = int.from_bytes(data[0:2], 'big')
        [opcode_bin,
         ea_mode_binary,
         ea_reg_bin] = split_bits(first_word, [10, 3, 3])

        if opcode_bin != 0b0100111010:
            return None

        if ea_mode_binary == 0b111:
            mode = EAMode.AWA if ea_reg_bin == 0 else EAMode.ALA
            dest = AssemblyParameter(mode, int.from_bytes(data[2:], byteorder='big', signed=False))
        elif ea_mode_binary == 0b010:
            dest = AssemblyParameter(EAMode.ARI, ea_reg_bin)
        else:
            return None

        return cls([dest])

    @classmethod
    def from_str(cls, command: str, parameters: str):
        """
        Parses a JSR command from text.

        >>> str(Jsr.from_str('JSR', '(A0)'))
        'Jsr command: dest EA Mode: EAMode.ARI, Data: 0'

        >>> str(Jsr.from_str('JSR', '($4000).W'))
        'Jsr command: dest EA Mode: EAMode.AWA, Data: 16384'

        :param command: The command itself (e.g. 'MOVE.B', 'LEA', etc.)
        :param parameters: The parameters after the command (such as the source and destination of a move)
        :return: The parsed command
        """
        return n_param_from_str(command, parameters, Jsr, 1, None)
