import json
import re

"""
List File

Represents the output from the assembler that contains all of the instructions and where in the
destination memory they should end up.
"""
MAX_MEMORY_LOCATION = 16777216  # 2^24

class ListFile:
    """
    Represents assembled instructions and their locations in memory
    """
    def __init__(self):
        """
        Constructor
        """
        # the keys of data must be strings so that they will work with JSON
        # but when working with it, integers are a lot cleaner and make more sense
        # so all of the interfaces that work with it are going to use ints
        # but internally it will use strings
        self.data = {}
        self.symbols = {}

    def insert_data(self, location: int, data: str):
        """
        Inserts the data at the given location into the list file
        This data should be a string of hexadecimal data
        :param location:
        :param data:
        :return:
        """
        assert location >= 0, 'Location is invalid!'
        assert location < MAX_MEMORY_LOCATION, 'Location is beyond possible bounds!'

        # ensure that the data is valid
        # loop through every 2 or 1 characters
        for s in re.findall('..?', data):
            # try to convert to an int of base 16
            # just to ensure that it is valid
            int(data, 16)

        self.data[str(location)] = data

    def insert_data_at_symbol(self, name: str, data: str):
        """
        Inserts the data at the location for the given symbol
        :param name:
        :param data:
        :return:
        """
        self.insert_data(self.get_symbol_location(name), data)

    def clear_location(self, location: int):
        """
        Clears the data at the given location
        :param location:
        :return:
        """
        assert location >= 0, 'Location is invalid!'
        assert location < MAX_MEMORY_LOCATION, 'Location is beyond possible bounds!'
        assert str(location) in self.data, 'Location not defined in data!'

        self.data.pop(str(location), None)

    def define_symbol(self, name: str, location: int):
        """
        Defines a label and it's associated location
        :param name:
        :param location:
        :return:
        """
        assert location >= 0, 'Location is invalid!'
        assert location < MAX_MEMORY_LOCATION, 'Location is beyond possible bounds!'

        # check that the symbol name is a single word
        assert re.match(r'^(([A-z])+([A-z]*[0-9]*))\w$', name), 'Symbol name was not a single word!'

        self.symbols[name] = location

    def clear_symbol(self, name: str):
        """
        Clears a label
        :param name:
        :return:
        """
        self.symbols.pop(name, None)

    def get_symbol_location(self, name: str) -> int:
        """
        Gets the associated location for a label
        :param name:
        :return: the location associated to the label, if it exists
        """
        assert name in self.symbols
        return self.symbols[name]

    def get_symbol_data(self, name: str) -> str:
        """
        Get the data for the given label
        Only works for the start of data
        This is not for reading in the middle of a set of data
        :param name:
        :return:
        """
        assert name in self.symbols, 'Symbol key was not in the labels dictionary'
        return self.get_starting_data(self.get_symbol_location(name))

    def get_starting_data(self, location: int) -> int:
        """
        Gets the data starting at the given location
        :param location:
        :return:
        """
        assert location >= 0, 'Location is invalid!'
        assert location < MAX_MEMORY_LOCATION, 'Location is beyond possible bounds!'
        assert str(location) in self.data, 'Location data not defined!'
        return self.data[str(location)]

    def to_json(self) -> str:
        """
        Dumps the current object into a JSON string
        :return:
        """
        ret = {}
        ret['data'] = self.data
        ret['symbols'] = self.symbols
        return json.dumps(ret, sort_keys=True)

    def load_from_json(self, json_str: str):
        """
        Populates this object from a json str
        :param json_str:
        :return:
        """
        loaded = json.loads(json_str)
        self.symbols = loaded['symbols']
        self.data = loaded['data']

    def __eq__(self, other) -> bool:
        """
        Equals operator
        :param other:
        :return:
        """
        return self.symbols == other.symbols and self.data == other.data

    def __ne__(self, other) -> bool:
        """
        Not equals operator
        :param other:
        :return:
        """
        return self.symbols != other.symbols or self.data != other.data