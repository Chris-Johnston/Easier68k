import json
import re

from .srecordtype import SRecordType

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
        self.starting_execution_address = 0

    def set_starting_execution_address(self, location: int):
        """
        Sets the starting execution address
        :param location:
        :return:
        """
        assert 0 <= location <= MAX_MEMORY_LOCATION, 'The starting execution address must be within the bounds [0, 2^24]!'
        self.starting_execution_address = location

    def get_starting_execution_address(self):
        """
        Gets the starting execution address
        :return:
        """
        return self.starting_execution_address

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
        ret['startingExecutionAddress'] = self.starting_execution_address
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
        self.starting_execution_address = loaded['startingExecutionAddress']

    def read_s_record_filename(self, filepath: str):
        """
        Read the S record at the given file path, builds the content of this list
        file from it
        :param filepath: {str} Path to an S record
        :return: None
        """
        with open(filepath, 'r') as f:
            for line in f:
                # process the line in the file
                self.__process_s_record_line(line)

    def __process_s_record_line(self, line: str):
        """
        Process a single line of the S record
        This is defined here: http://www.easy68k.com/easy68ksrecord.htm
        :param line: {str} a single line of an S record file
        :return: None
        """
        line = line.replace('\r', '').replace('\n', '')
        # type of record
        record_type = SRecordType.parse(line[:2])
        # count of remaining character pairs in the record
        count = int(line[2:4], 16)
        # address 2 3 or 4 bytes as hex
        address_val_len = 0

        if record_type is SRecordType.S0:
            # address field is unused
            address_val_len = 4
        elif record_type is SRecordType.S1:
            # 2 bytes
            address_val_len = 4
        elif record_type is SRecordType.S2:
            # 3 bytes
            address_val_len = 6
        elif record_type is SRecordType.S3:
            # 4 bytes
            address_val_len = 8
        elif record_type is SRecordType.S5:
            # the address field is interpreted as a 2 byte value
            # and contains the counts of S1 2 and 3 records prev
            # transmitted
            address_val_len = 4
        elif record_type is SRecordType.S7:
            # termination record
            # contains the starting execution address
            # as 4 bytes
            address_val_len = 8
        elif record_type is SRecordType.S8:
            # termination record
            # contains the starting execution address
            # as 3 bytes
            address_val_len = 6
        elif record_type is SRecordType.S9:
            # termination record
            # contains the starting execution address
            # as 2 bytes
            address_val_len = 4

        # get the address for the data
        address = int(line[4:4+address_val_len], 16)

        # get the data that should be between 0-64 characters
        data = line[4+address_val_len:-2]

        # the last two characters as a hexadecimal value
        # with the least significant byte of the ones complement of the sum
        # of the byte values represented by the pairs of characters
        # making up the count, address and data pairs

        # for now, I don't care about the checksum
        checksum = line[-2:]

        if record_type in [SRecordType.S1, SRecordType.S2, SRecordType.S3]:
            self.insert_data(address, data)

        if record_type in [SRecordType.S7, SRecordType.S8, SRecordType.S9]:
            self.starting_execution_address = address

    def __eq__(self, other) -> bool:
        """
        Equals operator
        :param other:
        :return:
        """
        return self.symbols == other.symbols and self.data == other.data and self.starting_execution_address == other.starting_execution_address

    def __ne__(self, other) -> bool:
        """
        Not equals operator
        :param other:
        :return:
        """
        return self.symbols != other.symbols or self.data != other.data