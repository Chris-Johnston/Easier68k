# -*- coding: utf-8 -*-

from ...core.enum.ea_mode import EAMode
from ...core.models.assembly_parameter import AssemblyParameter
from ...core.enum import ea_mode_bin
from ...core.enum.ea_mode_bin import parse_ea_from_binary
from ...simulator.m68k import M68K
from ...core.opcodes.opcode import Opcode
from ...core.util import opcode_util
from ...core.enum.op_size import OpSize
from ..util.parsing import parse_assembly_parameter
from ..util.split_bits import split_bits

# makes TC way easier lol
from bitstring import Bits

COND_CODE_TO_OPCODE = {
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
    pass


class branch_code(Opcode):
    """
    All Branch operations will inherit from branch_code. 
    there will be a conditional function to be overidden across child classes
    one must also redefine self.cond_code across child classes
    Additionally, a redefinition of command_matches() will suffice
    """

    operand = None
    address = None
    cond_code = None
    offset = None
    
    def __init__(self, params: list):
        assert len(params) == 3
        assert isinstance(params[0], AssemblyParameter) # Offset
        assert isinstance(params[1], int) # Address of this isntruction
        assert isinstance(params[2], OpSize)
        assert params[0].mode == EAMode.Immediate
        
        # Operand = target address
        self.operand = params[0]
        self.address = params[1]
        self.size = params[2]
        
    def conditional(self, simulator: M68K):
        """
        This is a method stub to be overridden in child classes
        Checks the status register according to the specifics of 
        whatever Bcc variant this is.
        :param simulator: the M68K sim object that contains the CCR we are checking
        :return bool: returns true or false 
        """
        raise Exception("Branch Operation did not override Parent's conditional stub")
        
    def assemble(self) -> bytearray:
        """
        Assembles opcode into Hex
        :return: Hex for this operation
        """
        
        # yes you actually need to subclass this
        assert self.cond_code != None
        
        # make offset out of operand
        self.offset = self.operand - self.address
        self.offset = Bits(int=self.offset, size=self.size)
        
        # clear for >8 bit offset
        lastbyte = '\x00'
        
        # if offset is 8 bits than it is inside the opword
        if self.size == OpSize.BYTE:
            lastbyte = self.offset.to_bytes()
        
        # if offset is 32 bits than the last chunk of opword is FF
        if self.size == OpSize.LONG:
            lastbyte = '\xFF'
            
        # first byte = 6+cond_code
        firstbyte =  6 << 4
        firstbyte &= self.cond_code.to_bytes()
        
        opword = firstbyte << 8
        opword &= lastbyte
        
        # stop here if 8 bit offset
        if self.size == OpSize.BYTE:
            return opword
            
        # add opword
        opword += self.offset.to_bytes(2, "big")
        
        return opword
    
    def execute(self, simulator: M68K):
        """
        Commands the Simulator according to this opcode
        :param simulator:
        :return: nothing
        """

        # check conditional
        if not self.conditional():
            pass
            
        simulator.increment_program_counter(self.offset + 2)
        
    @classmethod            
    def __str__(self):
        """
        converts command to a string
        :return: string rep of command
        """
        
        return "{s} ${d}".format(
                s = COND_CODE_TO_OPCODE.get(self.cond_code),
                d = (self.address + 2 + (self.size if self.size > 1 else 0) + self.offset) )

    @classmethod
    def command_matches(cls, command: str) -> bool:
        """
        Checks whether a command string is an instance of this command type
        :param command: The command string to check (e.g. 'MOVE.B', 'LEA', etc.)
        :return: Whether the string is an instance of this command type
        """
        
        return opcode_util.command_matches(command, COND_CODE_TO_OPCODE.get(self.cond_code))
    
    @classmethod
    def get_word_length(cls, command: str, parameters: str) -> int:
        """
        Gets what the end length of this command will be in memory
        :param command: The text of the command itself (e.g. "LEA", "MOVE.B", etc.)
        :param parameters: The parameters after the command
        :return: The length of the bytes in memory in words
        """
        
        # opword
        length = 2
        
        # BIG NOTE: I am explicitly ignoring size codes because there are no defined flippy boys
        # in the opword for Bcc ops. Yeezy68k might let you define a size code, but even it
        # will more or less ignore whatever you put (reduces unnessesary .l to .w)
        
        parameter = parameters.split(',')[0]
        
        # Check range of operand
        parameter = parse_assembly_parameter(parameter.strip())
        
        if parameter.mode = EAMode.AWA:
            length += 2
        if parameter.mode = EAMode.ALA:
            length += 4
        
        return length
    
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
        parameters = patameters.split(',')
        
        # See the BIG HORKIN' NOTE from get_word_length()
        # check param length
        if len(parameters) >1:
            passes = False
            errors.append("Too many operands for Branch Operation (TODO: list them here)")
        
        # check offset dest validity (odd read)
        offset = parse_assembly_parameter(parameters[0].strip())
        if offset.data % 2 == 1:
            passes = False
            errors.append("Reading word at {d} will cause crash".format(d=offset.data))
            
        return (passes, errors)