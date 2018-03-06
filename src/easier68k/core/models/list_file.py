import json

"""
List File

Represents the output from the assembler that contains all of the instructions
"""
MAX_MEMORY_LOCATION = 16777216  # 2^24

class ListFile:
    def __init__(self):
        """
        Constructor
        """
        self.data = {}
        self.labels = {}

    def insert_data(self, location: int, data: str) -> (int, str):
        """
        Inserts the data at the given location into the list file
        This data should be a string of hexadecimal data
        :param location:
        :param data:
        :return:
        """
        assert location >= 0
        assert location < MAX_MEMORY_LOCATION

        self.data[location] = data

    def clear_location(self, location: int) -> int:
        """
        Clears the data at the given location
        :param location:
        :return:
        """
        self.data[location] = None