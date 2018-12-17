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

"""
All Branch operations will inherit from branch_code. 
there will be a conditional function to be overidden across child classes
"""

class branch_code(Opcode):
    pass


class branch_code(Opcode):
    operand = None
    address = None
    cond_code = None
    
    def __init__(self, params: list):
        assert len(params) == 3
        assert isinstance(params[0], AssemblyParameter) # Offset
        assert isinstance(params[1], int) # Address
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
        assert cond_code != None
        
        # make offset out of operand
        self.offset = operand - address
        self.offset = Bits(int=offset, size=self.size)
        
        # clear for >8 bit offset
        lastbyte = '\x00'
        
        # if offset is 8 bits than it is inside the opword
        if self.size == OpSize.BYTE:
            lastbyte = offset.to_bytes()
        
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
        
        # add word of 0000 if 32 bit offset
        if self.size == OpSize.LONG:
            opword += '\x00\x00'
            
        # add opword
        opword += offset.to_bytes(2, "big")
        
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
            
        # twos comp if negative
        if offset < 0:
            if self.size = OpSize.Byte:
                
            