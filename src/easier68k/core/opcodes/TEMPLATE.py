from ...simulator.m68k import M68K

# Allowed values: nothing, or some combination of B, W, and L (for byte, word, and long)
# For example, MOVE would have 'BWL' because it can operate on any size of data, while MOVEA would have 'WL' because
# it can't operate on byte-sized data
allowed_sizes = 'BWL'


class TEMPLATE:
    # Include parameters here

    def assemble(self) -> bytearray:
        pass

    def execute(self, simulator: M68K):
        pass


def get_byte_length(command: str, parameters: str) -> (int, list):
    """
    Gets what the end length of this command will be in memory
    :param command: The text of the command itself (e.g. "LEA", "MOVE.B", etc.)
    :param parameters: The parameters after the command
    :return: The length of the bytes in memory, as well as a list of warnings or errors encountered
    """
    pass


def assemble(command: str, parameters: str) -> (TEMPLATE, list):
    """
    Assembles the given parameters into binary suitable for writing to memory
    :param command: The text of the command itself (e.g. "LEA", "MOVE.B", etc.)
    :param parameters: The parameters after the command
    :return: The bytes to write, as well as a list of warnings or errors encountered
    """
    pass