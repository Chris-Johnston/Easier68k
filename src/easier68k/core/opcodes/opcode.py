from ...simulator.m68k import M68K


# Outside the class so we can access it easier
def command_matches(command: str) -> bool:
    """
    Checks whether a command string is an instance of this command type
    :param command: The command string to check (e.g. 'MOVE.B', 'LEA', etc.)
    :return: Whether the string is an instance of this command type
    """
    pass


class_name = 'Opcode'

class Opcode:
    def assemble(self) -> bytearray:
        """
        Assembles this opcode into hex to be inserted into memory
        :return: The hex version of this opcode
        """
        pass

    def execute(self, simulator: M68K):
        """
        Executes this command in a simulator
        :param simulator: The simulator to execute the command on
        :return: Nothing
        """
        pass

    def __str__(self):
        return "Generic command base"

