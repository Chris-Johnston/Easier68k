from ..opcodes.opcode import Opcode
from ...simulator.m68k import M68K
from ..util.parsing import parse_assembly_parameter, from_str_util
from ..util.split_bits import split_bits
from ..models.trap_vector import TrapVector
from ..enum.ea_mode import EAMode

class Trap(Opcode): # forward declaration
    pass

class Trap(Opcode):

    def __init__(self, param: TrapVector):
        assert isinstance(param, TrapVector)
        # max size is 4 bit
        assert 0 <= param.get_value() <= 0b1111
        self.task = param

    def assemble(self) -> bytearray:
        """
        Assembles this opcode into hex to be inserted
        into memory
        :return:
        """
        # the bottom 4 bits are set to 0
        value = 0b0100111001000000

        # mask the task to fit in 4 bits
        masked = self.task & 0b1111

        # add the masked bits
        value |= masked

        # convert this value into a bytearray of len = 1 word
        return int.from_bytes(2, byteorder='big', signed=False)

    def execute(self, simulator: M68K):
        """
        Executes this command in a simulator
        :param simulator:
        :return:
        """
        pass

    def __str__(self):
        return 'TRAP {}'.format(self.task)

    @classmethod
    def from_str(cls, command: str, parameters: str):
        """
        Parses a TRAP command from text

        >>> str(Trap.from_str('TRAP', '#15'))
        'TRAP EA Mode: EAMode.IMM, Data: 15'

        >>> str(Trap.from_str('trap', '#%1110'))
        'TRAP EA Mode: EAMode.IMM, Data: 14'

        :param command:
        :param parameters:
        :return:
        """

        assert command.upper() == 'TRAP'

        # dont care about the size and parts values
        size, params, parts = from_str_util(command, parameters)

        assert len(params) == 1

        return cls(parse_assembly_parameter(params[0]))

    @classmethod
    def disassemble_instruction(cls, data: bytearray) -> Opcode:
        """
        Parses raw data into an instance of Trap
        :param data:
        :return:
        """

        assert len(data) == 2, 'Size must be 1 word'

        [opcode_bin, task_num] = split_bits(
            int.from_bytes(data, byteorder='big', signed=False),
            [12, 4])

        # didnt match
        if opcode_bin != 0b010011100100:
            return None

        # dont need to check that the size is valid, within 4 bits is ok
        # though some may not do anything

        return cls(TrapVector(task_num))