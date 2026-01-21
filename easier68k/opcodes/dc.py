from .opcode import Opcode
from ..op_size import OpSize
from ..m68k import M68K
from ..parsing import parse_literal
from itertools import zip_longest
import math
from ..opcode_util import check_valid_command, n_param_is_valid, n_param_from_str, command_matches


class DC(Opcode):
    valid_sizes = [OpSize.BYTE, OpSize.WORD, OpSize.LONG]
    QUOTE_DELIMETER = "'"

    def __init__(self, values: list, size=OpSize.WORD):
        assert size in DC.valid_sizes
        self.size = size

        assert len(values) > 0
        self.values = values

    def assemble(self) -> bytearray:
        """
        Assembles this opcode into hex to be inserted into memory
        :return: The hex version of this opcode
        """
        tr = ''
        for val in self.values:
            tr += '{0:08b}'.format(val)

        return bytearray.fromhex(hex(int(tr, 2))[2:])  # Convert to a bytearray

    def execute(self, simulator: M68K):
        """
        Executes this command in a simulator
        :param simulator: The simulator to execute the command on
        :return: Nothing
        """

        # DC does not implement execute because it is processed in the
        # assembly stage and effectively removed
        pass

    def __str__(self):
        return "DC command: Size {}, items: {}".format(self.size, self.values)

    @classmethod
    def command_matches(cls, command: str) -> bool:
        """
        Checks whether a command string is an instance of this command type
        :param command: The command string to check (e.g. 'MOVE.B', 'LEA', etc.)
        :return: Whether the string is an instance of this command type
        """
        return command_matches(command, 'DC')

    @classmethod
    def get_word_length(cls, command: str, parameters: str) -> int:
        """
        Gets the final length of a command in memory in words
        NOTE: for DC.B, this will round UP to make it a full word, even though it won't use the full memory

        >>> DC.get_word_length('DC.B', '$0A, $0B')
        1

        >>> DC.get_word_length('DC.W', '$0A, $0B')
        2

        >>> DC.get_word_length('DC.L', '$0A, $0B')
        4

        >>> DC.get_word_length('DC.B', '\\'Hai!\\'')
        2

        >>> DC.get_word_length('DC.W', '\\'Hai!\\'')
        2

        >>> DC.get_word_length('DC.L', '\\'Hai!\\'')
        4

        :param command: The command itself (e.g. 'MOVE.B', 'LEA', etc.)
        :param parameters:  The parameters after the command (such as the source and destination of a move)
        :return: The length of the command in memory (in words)
        """
        valid, issues = cls.is_valid(command, parameters)
        assert valid, 'Invalid command'
        # We're good without asserts from here on out

        parts = command.split('.')  # Split the command by period to get the size of the command
        if len(parts) == 1:  # Use the default size
            size = OpSize.WORD
        else:
            size = OpSize.parse(parts[1])

        length = 0
        in_quote = False
        current_param = ''
        is_string = False

        lookahead_iter = zip_longest(parameters, parameters[1:])

        for c, c_next in lookahead_iter:
            if c == ',' and not in_quote:  # End of this parameter (and not a comma in a quote)
                if current_param:
                    if is_string:
                        length += len(current_param) * 0.5
                        if len(current_param) % 2 != 0:
                            length += 1
                    else:
                        if size == OpSize.BYTE:
                            length += 0.5
                        elif size == OpSize.WORD:
                            length += 1
                        elif size == OpSize.LONG:
                            length += 2

                in_quote = False
                current_param = ''
                is_string = False
                continue

            if c == DC.QUOTE_DELIMETER:
                # This is the start or end of a quote (not an escaped apostrophe)
                if not in_quote:
                    in_quote = True
                    is_string = True
                    continue
                else:
                    if c_next == DC.QUOTE_DELIMETER:  # This is an escaped apostrophe in a string literal
                        current_param += DC.QUOTE_DELIMETER
                        next(lookahead_iter)  # Skip the other apostrophe so we don't double-process it
                        continue

                    # This is the end of a quote (not an escaped apostrophe)
                    in_quote = False
                    continue

            current_param += c

        if current_param:
            if is_string:
                length += len(current_param) * 0.5
                if len(current_param) % 2 != 0:
                    length += 1
            else:
                if size == OpSize.BYTE:
                    length += 0.5
                elif size == OpSize.WORD:
                    length += 1
                elif size == OpSize.LONG:
                    length += 2

        length = math.ceil(length)
        if size == OpSize.LONG and length % 4 != 0:
            length = length + (length % 4)

        return length

    @classmethod
    def is_valid(cls, command: str, parameters: str) -> (bool, list):
        """
        Tests whether the given command is valid

        >>> DC.is_valid('DC.B', '\\'Hello, world!\\'')[0]
        True

        >>> DC.is_valid('DC.B', '\\'Hello\\'\\' world!\\'')[0]
        True

        >>> DC.is_valid('DC.W', '\\'Hello\\', \\' world!\\'')[0]
        True

        >>> DC.is_valid('DC.W', '$0A, $0B')[0]
        True

        >>> DC.is_valid('DC.L', '$0A')[0]
        True

        >>> DC.is_valid('DC.B', '')[0]
        False

        >>> DC.is_valid('DC.W', '\\'Hey!\\', $0A')[0]
        True

        >>> DC.is_valid('DC.G', '$0A')[0]
        False

        :param command: The command itself (e.g. 'MOVE.B', 'LEA', etc.)
        :param parameters: The parameters after the command (such as the source and destination of a move)
        :return: Whether the given command is valid and a list of issues/warnings encountered
        """
        issues = []
        try:
            assert check_valid_command(command, 'DC', valid_sizes=DC.valid_sizes), 'Command invalid'

            param_count = 0
            in_quote = False
            current_param = ''
            is_string = False

            lookahead_iter = zip_longest(parameters, parameters[1:])

            for c, c_next in lookahead_iter:
                if c == ',' and not in_quote:  # End of this parameter (and not a comma in a quote)
                    if current_param:
                        if not is_string:  # Try parsing this value for a literal (if it's a string it's almost certainly fine)
                            assert parse_literal(current_param.strip()) is not None, 'Error parsing literal'
                        param_count += 1

                    in_quote = False
                    current_param = ''
                    is_string = False
                    continue

                if c == DC.QUOTE_DELIMETER:
                    # This is the start or end of a quote (not an escaped apostrophe)
                    if not in_quote:
                        assert not current_param, 'Expected comma between two string literals'
                        in_quote = True
                        is_string = True
                        continue
                    else:
                        if c_next == DC.QUOTE_DELIMETER:  # This is an escaped apostrophe in a string literal
                            current_param += DC.QUOTE_DELIMETER
                            next(lookahead_iter)  # Skip the other apostrophe so we don't double-process it
                            continue

                        # This is the end of a quote (not an escaped apostrophe)
                        in_quote = False
                        continue

                if c != ' ' or (c == ' ' and in_quote):  # Don't add spaces unless we're in a quote
                    current_param += c

            assert not in_quote, 'Expected apostrophe to end quote, got end of line instead'

            if current_param:
                if not is_string:
                    # Make the value the right hex length
                    assert parse_literal(current_param.strip()) is not None, 'Error parsing literal'

                param_count += 1

            assert param_count > 0, 'Must have at least one parameter'

        except AssertionError as e:
            issues.append((e.args[0], 'ERROR'))
            return False, issues

        return True, issues

    @classmethod
    def from_binary(cls, data: bytearray):
        return None, 0

    @classmethod
    def from_str(cls, command: str, parameters: str):
        """
        Parses a command string into an instance of the opcode class

        >>> test0 = DC.from_str("DC.B", "$0A, $0B")
        >>> test0.size
        <OpSize.BYTE: 1>
        >>> test0.values
        [10, 11]

        >>> test1 = DC.from_str("DC.B", "\\'Hai!\\'")
        >>> test1.size
        <OpSize.BYTE: 1>
        >>> test1.values
        [72, 97, 105, 33]

        >>> test2 = DC.from_str("DC.L", "\\'Hai\\'")
        >>> test2.size
        <OpSize.LONG: 4>
        >>> test2.values
        [72, 97, 105, 0]

        >>> test3 = DC.from_str("DC.L", "\\'Hai\\', $AB")
        >>> test3.size
        <OpSize.LONG: 4>
        >>> test3.values
        [72, 97, 105, 0, 0, 0, 0, 171]

        >>> test4 = DC.from_str("DC.W", "\\'Hai\\', $AB")
        >>> test4.size
        <OpSize.WORD: 2>
        >>> test4.values
        [72, 97, 105, 0, 0, 171]

        :param command: The command itself (e.g. 'MOVE.B', 'LEA', etc.)
        :param parameters: The parameters after the command (such as the source and destination of a move)
        """
        valid, issues = cls.is_valid(command, parameters)
        assert valid, 'Invalid command'
        # We're good without asserts from here on out

        parts = command.split('.')  # Split the command by period to get the size of the command
        if len(parts) == 1:  # Use the default size
            size = OpSize.WORD
        else:
            size = OpSize.parse(parts[1])

        params = []
        in_quote = False
        current_param = ''
        is_string = False

        lookahead_iter = zip_longest(parameters, parameters[1:])

        for c, c_next in lookahead_iter:
            if c == ',' and not in_quote:  # End of this parameter (and not a comma in a quote)
                if current_param:
                    if is_string:
                        temp_params = []
                        for char in current_param:
                            temp_params.append(ord(char))

                        # Right pad the string with zeroes
                        if size == OpSize.LONG:
                            if len(temp_params) % 4 != 0:
                                temp_params.extend(0 for _ in range(4 - (len(temp_params) % 4)))
                        if size == OpSize.WORD:
                            if len(temp_params) % 2 != 0:
                                temp_params.append(0)

                        params.extend(temp_params)
                    else:
                        # Make the value the right hex length
                        val = parse_literal(current_param.strip())
                        hexed = hex(val)[2:].upper()
                        if size == OpSize.LONG:
                            if len(hexed) % 8 != 0:
                                hexed = ('0' * (8 - (len(hexed) % 8))) + hexed

                        if size == OpSize.WORD:
                            if len(hexed) % 4 != 0:
                                hexed = ('0' * (4 - (len(hexed) % 4))) + hexed

                        if size == OpSize.BYTE:
                            if len(hexed) % 2 != 0:
                                hexed = '0' + hexed

                        # Length is now for sure even
                        for i in range(0, len(hexed), 2):
                            params.append(int(hexed[i:i+2], 16))

                in_quote = False
                current_param = ''
                is_string = False
                continue

            if c == DC.QUOTE_DELIMETER:
                # This is the start or end of a quote (not an escaped apostrophe)
                if not in_quote:
                    in_quote = True
                    is_string = True
                    continue
                else:
                    if c_next == DC.QUOTE_DELIMETER:  # This is an escaped delimeter in a string literal
                        current_param += DC.QUOTE_DELIMETER
                        next(lookahead_iter)  # Skip the other delimeter so we don't double-process it
                        continue

                    # This is the end of a quote (not an escaped apostrophe)
                    in_quote = False
                    continue

            current_param += c

        if current_param:
            if is_string:
                temp_params = []
                for char in current_param:
                    temp_params.append(ord(char))

                # Right pad the string with zeroes
                if size == OpSize.LONG:
                    if len(temp_params) % 4 != 0:
                        temp_params.extend(0 for _ in range(4 - (len(temp_params) % 4)))
                if size == OpSize.WORD:
                    if len(temp_params) % 2 != 0:
                        temp_params.append(0)

                params.extend(temp_params)
            else:
                # Make the value the right hex length
                val = parse_literal(current_param.strip())
                hexed = hex(val)[2:].upper()
                if size == OpSize.LONG:
                    if len(hexed) % 8 != 0:
                        hexed = ('0' * (8 - (len(hexed) % 8))) + hexed

                if size == OpSize.WORD:
                    if len(hexed) % 4 != 0:
                        hexed = ('0' * (4 - (len(hexed) % 4))) + hexed

                if size == OpSize.BYTE:
                    if len(hexed) % 2 != 0:
                        hexed = '0' + hexed

                # Length is now for sure even
                for i in range(0, len(hexed), 2):
                    params.append(int(hexed[i:i + 2], 16))

        return cls(params, size)

    @classmethod
    def disassemble_instruction(cls, data: bytes) -> Opcode:
        """
        Disassembles the instuction into an instance of the DC class
        """
        # DC is a directive for the assembler, so it has no representaiton
        # as bytes
        pass

        