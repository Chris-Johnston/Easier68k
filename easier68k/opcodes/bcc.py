# -*- coding: utf-8 -*-

from .opcode import Opcode
from ..condition_status_code import ConditionStatusCode
from ..m68k import M68K
from ..parsing import *

# makes TC way easier lol
from bitstring import Bits
from math import log
from abc import ABC, ABCMeta, abstractmethod
from ..opcode_util import check_valid_command, n_param_is_valid, n_param_from_str

COND_CODE_TO_OPCODE = {
    '\x00': 'BRA',
    '\x02': 'BHI',
    '\x03': 'BLS',
    '\x04': 'BCC',
    '\x05': 'BCS',
    '\x06': 'BNE',
    '\x07': 'BEQ',
    '\x08': 'BVC',
    '\x09': 'BVS',
    '\x0A': 'BPL',
    '\x0B': 'BMI',
    '\x0C': 'BGE',
    '\x0D': 'BLT',
    '\x0E': 'BGT',
    '\x0F': 'BLE'
}

class branch_code(Opcode):
    """
    All Branch operations will inherit from branch_code.
    there will be a conditional function to be overidden across child classes
    one must also redefine self.cond_code across child classes
    Additionally, a redefinition of command_matches(), from_str(), and disassemble_instruction() will suffice


    BCC:     Operation: If Condition True Then PC + dn → PC

    Syntax:  Bcc < label >

    Size = (Byte, Word, Long*)
    *(MC68020, MC68030, and MC68040 only)

    Description: If the specified condition is true, program execution continues at location (PC) + displacement. The program counter contains the address of the instruction word for
    the Bcc instruction plus two. The displacement is a twos-complement integer that
    represents the relative distance in bytes from the current program counter to the
    destination program counter. If the 8-bit displacement field in the instruction word is
    zero, a 16-bit displacement (the word immediately following the instruction) is used. If
    the 8-bit displacement field in the instruction word is all ones ($FF), the 32-bit
    displacement (long word immediately following the instruction) is used. Condition code
    cc specifies one of the following conditional tests (refer to Table 3-19 for more
                                                         information on these conditional tests):

    Condition Codes:    Not affected.

    Instruction Fields:
        Condition field—The binary code for one of the conditions listed in the table.
        8-Bit Displacement field—Twos complement integer specifying the number of bytes
            between the branch instruction and the next instruction to be executed if the
            condition is met.
        16-Bit Displacement field—Used for the displacement when the 8-bit displacement
            field contains $00.
        32-Bit Displacement field—Used for the displacement when the 8-bit displacement
            field contains $FF.

    NOTE    A branch to the immediately following instruction automatically
    uses the 16-bit displacement format because the 8-bit
    displacement field contains $00 (zero offset).
    """

    operand = None
    address = None
    cond_code = None
    offset = None
    size = None
    
    def __init__(self, params: list):
        assert len(params) == 2
        assert isinstance(params[0], int)
        assert isinstance(params[1], int)

        # Operand = target address
        self.operand = params[0]
        self.address = params[1]

        # make offset out of operand
        self.offset = int(self.operand) - int(self.address + 2)

        # get the size
        self.size = OpSize.BYTE if int(self.offset) < 128 else \
            (OpSize.WORD if int(self.offset) < 326778 else OpSize.LONG)

        # offset to bits
        self.offset = Bits(int=self.offset,
                           length=(self.size.get_number_of_bytes() * 8)).int

        # Note on Page 130 of the NXP 68K Manual
        # 0x00 8 bit offset defaults to word size
        if self.offset == 0:
            self.size = OpSize.WORD

    @abstractmethod
    def conditional(self, simulator: M68K):
        """
        This is a method stub to be overridden in child classes
        Checks the status register according to the specifics of 
        whatever Bcc variant this is.
        :param simulator: the M68K sim object that contains the CCR we are checking
        :return bool: returns true or false 
        """
        raise NotImplementedError("Branch Operation did not override Parent's conditional stub")
        
    def assemble(self) -> bytearray:
        """
        Assembles opcode into Hex
        :return: Hex for this operation
        """
        
        # yes you actually need to subclass this
        assert self.cond_code != None, 'No cond_code, assemble called on base clas of branch op?'

        # hold size
        extraSize = 2
        
        # clear for >8 bit offset
        lastbyte = '\x00'
        
        # if offset is 8 bits than it is inside the opword
        if self.size == OpSize.BYTE:
            lastbyte = self.offset.to_bytes(length=1, byteorder='big', signed=True)
            extraSize = 0

        # if offset is 32 bits than the last chunk of opword is FF
        if self.size == OpSize.LONG:
            lastbyte = '\xFF'
            extraSize = 4
            
        # first byte = 6+cond_code
        firstbyte =  ord('\x60')
        firstbyte |= ord(self.cond_code)
        
        opword = firstbyte << 8
        opword |= ord(lastbyte)

        # convert to bytearray
        opword = bytearray(opword.to_bytes(2, 'big'))

        # stop here if 8 bit offset
        if self.size == OpSize.BYTE:
            return opword

        # add offset
        opword.extend(self.offset.to_bytes(extraSize, "big"))

        return opword

    
    def execute(self, simulator: M68K):
        """
        Commands the Simulator according to this opcode
        :param simulator:
        :return: nothing
        """

        # check conditional
        if self.conditional(simulator):
            self.offset += 2
            simulator.increment_program_counter(self.offset)

    def __str__(self):
        """
        converts command to a string
        :return: string rep of command
        """

        return "{s} ${d}".format(
                s = COND_CODE_TO_OPCODE.get(self.cond_code),
                d = hex(self.operand or
                     (self.address + (self.size if self.size.get_number_of_bytes() > 1 else 0) + self.offset)))

    @classmethod
    @abstractmethod
    def command_matches(cls, command: str) -> bool:
        """
        Checks whether a command string is an instance of this command type
        :param command: The command string to check (e.g. 'MOVE.B', 'LEA', etc.)
        :return: Whether the string is an instance of this command type
        """
        raise NotImplementedError("Branch Operation did not override parent class command_matches stub!")

    @classmethod
    def get_word_length(cls, command: str, parameters: str) -> int:
        """
        Gets what the end length of this command will be in memory
        :param command: The text of the command itself (e.g. "LEA", "MOVE.B", etc.)
        :param parameters: The parameters after the command
        :return: The length of the bytes in memory in words
        """
        
        # BIG NOTE: I am explicitly ignoring size codes because there are no defined flippy boys
        # in the opword for Bcc ops. Yeezy68k might let you define a size code, but even it
        # will more or less ignore whatever you put (reduces unnessesary .l to .w)

        parameters = parameters.split(',')
        for i in parameters:
            i = i.strip()

        parameters[0] = parse_literal(parameters[0])
        parameters[1] = int(parameters[1])

        offutilset = abs(int(parameters[0]) - int(parameters[1] + 2))
        size = 1 if offset < 128 else (2 if offset < 326778 else 3)

        return size
    
    @classmethod
    def is_valid(cls, command: str, parameters: str) -> (bool, list):
        """
        Tests whether the given command is valid

        :param command: The command itself (e.g. 'MOVE.B', 'LEA', etc.)
        :param parameters: The parameters after the command (such as the source and destination of a move)
        :return: Whether the given command is valid and a list of issues/warnings encountered
        """
        
        passes = True
        errors = []
        parameters = parameters.split(',')
        
        # See the BIG NOTE from get_word_length()
        # check param length
        if len(parameters) > 1:
            passes = False
            errors.append("Too many operands for Branch Operation: " + ', '.join(parameters))
        
        # check offset dest validity (odd read)
        operand = parse_literal(parameters[0].strip())
        if operand % 2 == 1:
            passes = False
            errors.append("Reading word at {d} will cause crash".format(d=operand))
            
        return (passes, errors)
    
    @classmethod
    def disassemble_instruction(cls, data: bytes) -> Opcode:
        """
        Parses some raw data into an instance of the opcode class

        :param data: The data used to convert into an opcode instance
        :return: The constructed instance or none if there was an error and
            the amount of data in words that was used (e.g. extra for immediate
            data) or 0 for not a match
        """
        raise NotImplementedError("Branch Operation did not override parent class disassemble_instruction stub!")


    @classmethod
    def from_str(cls, command: str, parameters: str):
        """
        Parses a command from text

        :param command: The command itself (e.g. 'MOVE.B', 'LEA', etc.)
        :param parameters: The parameters after the command (such as the source and destination of a move)
        :param address: Address of this operation 
        :return: The parsed command
        """
        raise NotImplementedError("Branch Operation did not override parent class from_str stub!")


# ================ GENERIC FUNCTIONS FOR CLASSMETHODS =========================
# All of this is re-entrant code so it has been refactored out here.

def bcc_disassemble_instruction(data: bytes, arg: type, arg_cond_code: int):
    """
    Parses some raw data into an instance of the opcode class

    :param data: The data used to convert into an opcode instance
    :param arg: The class of BCC to be used
    :param arg_cond_code: The condition byte of the BCC instruction
    :return: The constructed instance or none if there was an error and
        the amount of data in words that was used (e.g. extra for immediate
        data) or 0 for not a match
    """

    fb = (6 << 4) | arg_cond_code
    if data[0] != fb:
        return 0

    valid_sizes = [2, 4, 6]
    if len(data) not in valid_sizes:
        return None

    offset = data[1]
    s = 1

    # check word size
    if offset == '\x00':
        offset = data[2:4]
        s = 2
        if not len(offset) == 2:
            return None

    elif offset == '\xFF':
        offset = data[2:6]
        s = 4
        if not len(offset) == 4:
            return None

    op = arg([0, 0]) # lol
    op.offset = int.from_bytes(bytes=offset.to_bytes(length=s, byteorder='big', signed=False),
                               byteorder='big',
                               signed=True) # couldnt think of a better way to sign this, I sure hope someone else does

    return op

def bcc_from_str(command: str, parameters: str, arg: type):
    """
    Parses a command from text

    :param command: The command itself (e.g. 'MOVE.B', 'LEA', etc.)
    :param parameters: The parameters after the command (such as the source and destination of a move)
    :param arg: class of this BCC
    :return: The parsed command
    """

    # Sanity Check!
    assert issubclass(arg, branch_code), 'bcc_from_str used on non branch opcode, what are you doing?'
    assert arg.command_matches(command), '[OPCODE] command_matches failed, from_str called!'

    # parameter to list
    parameters = parameters.split(',')
    for i in parameters:
        i = i.strip()

    # operand
    parameters[0] = parse_literal(parameters[0])

    # address
    parameters[1] = int(parameters[1])


    return arg(parameters)

# =============================================================================

# Illegal zone, all code here will be arrested by police officers

# ============================== OVERLOADS ====================================

class Bra(branch_code):
    """
    The BRA opcode, compiles to 60xx xxxx xxxx
    the conditional here is True, always.
    """
    cond_code = '\x00'

    def conditional(self, simulator: M68K):
        return True

    @classmethod
    def command_matches(cls, command: str):
        return command_matches(command, 'BRA')

    @classmethod
    def disassemble_instruction(cls, data: bytes):
        return bcc_disassemble_instruction(data, Bra, 0)

    @classmethod
    def from_str(cls, command: str, parameters: str):
        return bcc_from_str(command, parameters, Bra)


class Bhi(branch_code):
    """
    The BHI opcode, compiles to 62xx xxxx xxxx
    The conditional here is NOT C AND NOT Z
    """

    cond_code = '\x02'

    def conditional(self, simulator: M68K):
        c = simulator.get_condition_status_code(ConditionStatusCode.C)
        z = simulator.get_condition_status_code(ConditionStatusCode.Z)

        if not c and not z:
            return True

        return False

    @classmethod
    def command_matches(cls, command: str):
        return command_matches(command, 'BHI')

    @classmethod
    def disassemble_instruction(cls, data: bytes):
        return bcc_disassemble_instruction(data, Bhi, 2)

    @classmethod
    def from_str(cls, command: str, parameters: str):
        return bcc_from_str(command, parameters, Bhi)


class Bls(branch_code):
    """
    The BLS opcode compiles down to 63xx xxxx xxxx
    The conditional here is C OR Z
    """

    cond_code = '\x03'

    def conditional(self, simulator: M68K):
        c = simulator.get_condition_status_code(ConditionStatusCode.C)
        z = simulator.get_condition_status_code(ConditionStatusCode.Z)

        if c or z:
            return True

        return False

    @classmethod
    def command_matches(cls, command: str):
        return command_matches(command, 'BLS')

    @classmethod
    def disassemble_instruction(cls, data: bytes):
        return bcc_disassemble_instruction(data, Bls, 3)

    @classmethod
    def from_str(cls, command: str, parameters: str):
        return bcc_from_str(command, parameters, Bls)


class Bcc(branch_code):
    """
    The BCC opcode compiles down to 64xx xxxx xxxx
    The conditional here is NOT C
    """

    cond_code = '\x04'

    def conditional(self, simulator: M68K):
        return not simulator.get_condition_status_code(ConditionStatusCode.C)

    @classmethod
    def command_matches(cls, command: str):
        return command_matches(command, 'BCC')

    @classmethod
    def disassemble_instruction(cls, data: bytes):
        return bcc_disassemble_instruction(data, Bcc, 4)

    @classmethod
    def from_str(cls, command: str, parameters: str):
        return bcc_from_str(command, parameters, Bcc)


class Bcs(branch_code):
    """
    The BCS opcode compiles down to 65xx xxxx xxxx
    The conditional here is C
    """

    cond_code = '\x05'

    def conditional(self, simulator: M68K):
        return simulator.get_condition_status_code(ConditionStatusCode.C)

    @classmethod
    def command_matches(cls, command: str):
        return command_matches(command, 'BCS')

    @classmethod
    def disassemble_instruction(cls, data: bytes):
        return bcc_disassemble_instruction(data, Bcs, 5)

    @classmethod
    def from_str(cls, command: str, parameters: str):
        return bcc_from_str(command, parameters, Bcs)


class Bne(branch_code):
    """
    The BNE opcode compiles down to 66xx xxxx xxxx
    The conditional here is NOT Z
    """

    cond_code = '\x06'

    def conditional(self, simulator: M68K):
        return not simulator.get_condition_status_code(ConditionStatusCode.Z)

    @classmethod
    def command_matches(cls, command: str):
        return command_matches(command, 'BNE')

    @classmethod
    def disassemble_instruction(cls, data: bytes):
        return bcc_disassemble_instruction(data, Bne, 6)

    @classmethod
    def from_str(cls, command: str, parameters: str):
        return bcc_from_str(command, parameters, Bne)


class Beq(branch_code):
    """
    The BEQ opcode compiles down to 67xx xxxx xxxx
    The conditional here is Z
    """

    cond_code = '\x07'

    def conditional(self, simulator: M68K):
        return simulator.get_condition_status_code(ConditionStatusCode.Z)

    @classmethod
    def command_matches(cls, command: str):
        return command_matches(command, 'BEQ')

    @classmethod
    def disassemble_instruction(cls, data: bytes):
        return bcc_disassemble_instruction(data, Beq, 7)

    @classmethod
    def from_str(cls, command: str, parameters: str):
        return bcc_from_str(command, parameters, Beq)


class Bvc(branch_code):
    """
    The BVC opcode compiles down to 68xx xxxx xxxx
    The conditional here is NOT V
    """

    cond_code = '\x08'

    def conditional(self, simulator: M68K):
        return not simulator.get_condition_status_code(ConditionStatusCode.V)

    @classmethod
    def command_matches(cls, command: str):
        return command_matches(command, 'BVC')

    @classmethod
    def disassemble_instruction(cls, data: bytes):
        return bcc_disassemble_instruction(data, Bvc, 8)

    @classmethod
    def from_str(cls, command: str, parameters: str):
        return bcc_from_str(command, parameters, Bvc)


class Bvs(branch_code):
    """
    The BVS opcode compiles down to 69xx xxxx xxxx
    The conditional here is V
    """

    cond_code = '\x09'

    def conditional(self, simulator: M68K):
        return simulator.get_condition_status_code(ConditionStatusCode.V)

    @classmethod
    def command_matches(cls, command: str):
        return command_matches(command, 'BVS')

    @classmethod
    def disassemble_instruction(cls, data: bytes):
        return bcc_disassemble_instruction(data, Bvs, 9)

    @classmethod
    def from_str(cls, command: str, parameters: str):
        return bcc_from_str(command, parameters, Bvs)


class Bpl(branch_code):
    """
    The BPL opcode compiles down to 6Axx xxxx xxxx
    The conditional here is NOT N
    """

    cond_code = '\x0A'

    def conditional(self, simulator: M68K):
        return not simulator.get_condition_status_code(ConditionStatusCode.N)

    @classmethod
    def command_matches(cls, command: str):
        return command_matches(command, 'BPL')

    @classmethod
    def disassemble_instruction(cls, data: bytes):
        return bcc_disassemble_instruction(data, Bpl, ord('\x0A'))

    @classmethod
    def from_str(cls, command: str, parameters: str):
        return bcc_from_str(command, parameters, Bpl)


class Bmi(branch_code):
    """
    The BMI opcode compiles down to 6Bxx xxxx xxxx
    The conditional here is N
    """

    cond_code = '\x0B'

    def conditional(self, simulator: M68K):
        return simulator.get_condition_status_code(ConditionStatusCode.N)

    @classmethod
    def command_matches(cls, command: str):
        return command_matches(command, 'BMI')

    @classmethod
    def disassemble_instruction(cls, data: bytes):
        return bcc_disassemble_instruction(data, Bmi, ord('\x0B'))

    @classmethod
    def from_str(cls, command: str, parameters: str):
        return bcc_from_str(command, parameters, Bmi)


class Bge(branch_code):
    """
    The BGE opcode compiles down to 6Cxx xxxx xxxx
    The conditional here is N AND V OR NOT N AND NOT V
    """

    cond_code = '\x0C'

    def conditional(self, simulator: M68K):
        n = simulator.get_condition_status_code(ConditionStatusCode.N)
        v = simulator.get_condition_status_code(ConditionStatusCode.V)

        return n == v

    @classmethod
    def command_matches(cls, command: str):
        return command_matches(command, 'BGE')

    @classmethod
    def disassemble_instruction(cls, data: bytes):
        return bcc_disassemble_instruction(data, Bge, ord('\x0C'))

    @classmethod
    def from_str(cls, command: str, parameters: str):
        return bcc_from_str(command, parameters, Bge)


class Blt(branch_code):
    """
    The BLT opcode compiles down to 6Dxx xxxx xxxx
    The conditional here is N AND NOT V OR NOT N AND V
    """

    cond_code = '\x0D'

    def conditional(self, simulator: M68K):
        n = simulator.get_condition_status_code(ConditionStatusCode.N)
        v = simulator.get_condition_status_code(ConditionStatusCode.V)

        return not n == v

    @classmethod
    def command_matches(cls, command: str):
        return command_matches(command, 'BLT')

    @classmethod
    def disassemble_instruction(cls, data: bytes):
        return bcc_disassemble_instruction(data, Blt, ord('\x0D'))

    @classmethod
    def from_str(cls, command: str, parameters: str):
        return bcc_from_str(command, parameters, Blt)


class Bgt(branch_code):
    """
    The BGT opcode compiles down to 6Exx xxxx xxxx
    The conditional here is N AND V AND NOT Z OR NOT N AND NOV AND NOT Z
    """

    cond_code = '\x0E'

    def conditional(self, simulator: M68K):
        n = simulator.get_condition_status_code(ConditionStatusCode.N)
        v = simulator.get_condition_status_code(ConditionStatusCode.V)
        z = simulator.get_condition_status_code(ConditionStatusCode.Z)

        return (n == v) and not z

    @classmethod
    def command_matches(cls, command: str):
        return command_matches(command, 'BGT')

    @classmethod
    def disassemble_instruction(cls, data: bytes):
        return bcc_disassemble_instruction(data, Bgt, ord('\x0E'))

    @classmethod
    def from_str(cls, command: str, parameters: str):
        return bcc_from_str(command, parameters, Bgt)


class Ble(branch_code):
    """
    The BLE opcode compiles down to 6Fxx xxxx xxxx
    The conditional here is (Z) OR (N AND NOT V) OR (NOT N AND V)
    """

    cond_code = '\x0F'

    def conditional(self, simulator: M68K):
        n = simulator.get_condition_status_code(ConditionStatusCode.N)
        v = simulator.get_condition_status_code(ConditionStatusCode.V)
        z = simulator.get_condition_status_code(ConditionStatusCode.Z)

        return (n != v) or z
        

    @classmethod
    def command_matches(cls, command: str):
        return command_matches(command, 'BLE')

    @classmethod
    def disassemble_instruction(cls, data: bytes):
        return bcc_disassemble_instruction(data, Ble, ord('\x0F'))

    @classmethod
    def from_str(cls, command: str, parameters: str):
        return bcc_from_str(command, parameters, Ble)

# ==============================================================================
