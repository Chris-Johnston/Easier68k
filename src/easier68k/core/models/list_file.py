"""
List File

Represents the output from the assembler that contains all of the instructions
"""

class ListFile:
    def __init__(self):
        """
        Construcctor

        The raw assembly instructions
        """
        self.content = bytearray([0x00])

    def load_bytes(self, bytes):
        """
        Loads the contents of a byte array
        into the contents of this list file
        :param bytes:
        :return:
        """
        self.content = bytes

    def load_from_str(self, bytestr: str) -> str:
        """
        Loads the contents of a string into the contents
        of this list file.
        :param bytestr:
        :return:
        """
        self.content = bytestr.encode('ascii')

    def load_easy68k_list_file(self, contents):
        """
        Populates the contents of this list file
        from an easy68k list file, and loads the
        raw assembly instructions into the content
        byte array.
        :param contents:
        :return:
        """
        # TODO implement the load_easy68k_list_file
        pass

    def load_raw_list_file(self, contents):
        """
        Populates the contents of this list file
        from a raw list file (without all the additions
        that easy68k adds), and loads the asembly instructions
        into the content of the byte array.
        :param contents:
        :return:
        """
        # TODO implement load_raw_list_file
        pass