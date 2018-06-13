from ...simulator.m68k import M68K


class Opcode:
    pass


class Opcode:
    def assemble(self) -> bytes:
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

    @classmethod
    def command_matches(cls, command: str) -> bool:
        """
        Checks whether a command string is an instance of this command type
        :param command: The command string to check (e.g. 'MOVE.B', 'LEA', etc.)
        :return: Whether the string is an instance of this command type
        """
        pass

    @classmethod
    def get_word_length(cls, command: str, parameters: str) -> int:
        """
        Gets what the end length of this command will be in memory
        :param command: The text of the command itself (e.g. "LEA", "MOVE.B", etc.)
        :param parameters: The parameters after the command
        :return: The length of the bytes in memory in words
        """
        pass

    @classmethod
    def is_valid(cls, command: str, parameters: str) -> (bool, list):
        """
        Tests whether the given command is valid

        :param command: The command itself (e.g. 'MOVE.B', 'LEA', etc.)
        :param parameters: The parameters after the command (such as the source and destination of a move)
        :return: Whether the given command is valid and a list of issues/warnings encountered
        """

    @classmethod
    def disassemble_instruction(cls, data: bytes) -> Opcode:
        """
        Parses some raw data into an instance of the opcode class

        :param data: The data used to convert into an opcode instance
        :return: The constructed instance or none if there was an error and
            the amount of data in words that was used (e.g. extra for immediate
            data) or 0 for not a match
        """
        pass

    @classmethod
    def from_str(cls, command: str, parameters: str):
        """
        Parses a command from text

        :param command: The command itself (e.g. 'MOVE.B', 'LEA', etc.)
        :param parameters: The parameters after the command (such as the source and destination of a move)
        :return: The parsed command
        """