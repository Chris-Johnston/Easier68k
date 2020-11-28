from abc import ABC, abstractmethod, abstractproperty
from typing import Optional
from .opcode_assembler import OpCodeAssembler
from .assembly_parameter import AssemblyParameter
from .ea_mode import EAMode
from .ea_mode_bin import EAModeBinary
from .op_size import Size, OpSize
from .m68k import M68K
from .register import Register
from .memory_value import MemoryValue
from .assembly_transformer import Literal

# bytes -> assembler tree find match -> add assembler
# add assembler -> add opcode -> execute

class OpCodeBase():

    # @abstractmethod
    def from_param_list(self, size: OpSize, values: list):
        """
        Initializes the opcode from the parameters provided.
        """
        self.size = size

    @abstractmethod
    def from_asm_values(self, values: list):
        """
        Initializes the opcode from the assembly values.
        """
        pass

    @abstractmethod
    def to_asm_values(self):
        """
        Gets the assembly values for the current state of the opcode,
        so that it can be passed on to the corresponding "assembler/disassembler" type,
        and so that the binary value can be created.
        """
        pass
    
    @abstractmethod
    def execute(self, cpu: M68K):
        pass

    def get_additional_data_length(self):
        """
        If the opcode has immediate data, gets the additional number of
        bytes to increment the PC by.
        """
        return 0
