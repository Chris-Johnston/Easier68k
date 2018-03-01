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

    def load_bytes(self, bytes: bytearray) -> bytearray:
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

    def load_easy68k_list_file(self, contents: str) -> str:
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

    def load_raw_list_file(self, contents: str) -> str:
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

    def _load_data_at_location(self, location: int, data) -> int:
        """
        Loads data into the location specified
        :param location:
        :param data:
        :return:
        """

        # convert the input into immutable bytes
        input_data = bytes(data)

        # offset from the starting location
        offset = 0

        # iterate through the input data
        for value in input_data:
            self.content[location + offset] = value
            # increment the offset
            offset += 1
