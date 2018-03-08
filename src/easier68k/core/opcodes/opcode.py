from ...simulator.m68k import M68K


class Opcode:
    @classmethod
    def from_str(cls, command: str, parameters: str):
        pass
    
    @classmethod
    def from_binary(cls, data: bytearray):
        """
        Parses some raw data into an instance of the opcode class
        :param data: The data used to convert into an opcode instance
        :return: The constructed instance or none if there was an error and
            the amount of data in words that was used (e.g. extra for immediate
            data) or 0 for not a match
        """
        pass

    @staticmethod
    def is_valid(command: str, parameters: str) -> (bool, list):
        """
        Tests whether the given command is valid
        :param command: The command itself (e.g. 'MOVE.B', 'LEA', etc.)
        :param parameters: The parameters after the command (such as the source and destination of a move)
        :return: Whether the given command is valid and a list of issues/warnings encountered
        """

    @staticmethod
    def get_word_length(command: str, parameters: str) -> (int, list):
        """
        Gets the final length of a command in memory in words
        :param command: The command itself (e.g. 'MOVE.B', 'LEA', etc.)
        :param parameters:  The parameters after the command (such as the source and destination of a move)
        :return: The length of the command in memory (in words) and a list of issues/warnings encountered during assembly
        """
        pass

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

